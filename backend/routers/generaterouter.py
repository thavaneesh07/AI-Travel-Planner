import datetime
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..schemas.generateschemas import GenerateRequest
from ..schemas.chatschemas import ChatEditRequest
from ..schemas.tripschemas import TripUpdateDayRequest
from ..ai.intentengine import TravelIntentEngine, REQUIREDTRIPFIELDS
from ..ai.structuredparser import clean_extracted_entities
from ..agents.travelassistantagent import TravelAssistantAgent
from ..agents.tripplanningagent import TripPlanningAgent
from ..services.itinerary.editor import ItineraryEditor
from ..services.routeoptimizer.optimizer import RouteOptimizer
from ..dependencies import get_current_user, oauth2_scheme
from ..models.trip import Trip
from ..models.tripday import TripDay
from ..models.activity import Activity
from ..models.budget import Budget

router = APIRouter(tags=["AI Generation & Editing"])

@router.post("/generate")
async def generate(req: GenerateRequest, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    current_user = None
    if token:
        try:
            current_user = get_current_user(token, db)
        except Exception:
            pass

    session_id = req.sessionid or str(uuid.uuid4())
    planning_state = req.planningstate or {"entities": {}}

    analysis = TravelIntentEngine.analyze(req.message, planning_state)
    intent = analysis.get("intent", "travelquestion")
    extracted_entities = analysis.get("entities", {})

    # Guard: If there is an active itinerary, prevent misclassifying questions as new trip planning
    if req.itinerary and intent == "plantrip":
        curr_dest = req.itinerary.get("destination", "").lower()
        ext_dest = (extracted_entities.get("destination") or "").lower()
        if not ext_dest or ext_dest == curr_dest:
            intent = "travelquestion"

    cleaned_new_entities = clean_extracted_entities(extracted_entities, req.message)

    is_planning_session = False
    if planning_state.get("entities", {}).get("destination"):
        missing = []
        for field in REQUIREDTRIPFIELDS:
            if not planning_state["entities"].get(field):
                missing.append(field)
        if missing:
            is_planning_session = True

    if is_planning_session:
        has_new_fields = False
        for k, v in cleaned_new_entities.items():
            if v is not None and v != "" and v != []:
                if not planning_state["entities"].get(k):
                    has_new_fields = True
                    break
        if has_new_fields:
            intent = "plantrip"

    if intent in ("non_travel", "nontravel"):
        ans = TravelAssistantAgent.answer(req.message, req.history or [], req.itinerary, intent="nontravel")
        return {
            "status": "success",
            "intent": "nontravel",
            "answer": ans
        }

    if intent in ("modifytrip", "modify_trip"):
        op = await ItineraryEditor.parse_edit_query(req.message)
        if not op or not op.get("operation"):
            ans = "I couldn't process the exact modification from your request. Could you specify which day and time slot to change (e.g., 'Change day 2 morning to the Louvre')?"
            return {
                "status": "success",
                "intent": "travelquestion",
                "answer": ans
            }

        itinerary_details = None
        trip = None
        trip_id_to_load = req.tripid
        if trip_id_to_load:
            trip = db.query(Trip).filter(Trip.id == trip_id_to_load).first()
            if trip:
                from .triprouter import get_trip_details
                itinerary_details = get_trip_details(trip)

        if not itinerary_details and req.itinerary:
            itinerary_details = req.itinerary

        if not itinerary_details:
            raise HTTPException(status_code=400, detail="No active itinerary found to modify.")

        updated_itinerary = await ItineraryEditor.apply_edit(itinerary_details, op)

        if trip:
            day_num = op.get("day")
            day_idx = int(day_num) - 1
            trip_days = sorted(trip.days, key=lambda d: d.day_number)
            if 0 <= day_idx < len(trip_days):
                target_day = trip_days[day_idx]
                
                db.query(Activity).filter(Activity.tripdayid == target_day.id).delete()
                db.commit()

                updated_day_data = updated_itinerary["days"][day_idx]
                target_day.estimated_cost = updated_day_data.get("estimatedcost", 0.0)
                target_day.routejson = updated_day_data.get("route")
                db.commit()

                for idx, act in enumerate(updated_day_data.get("activities", [])):
                    new_act = Activity(
                        tripdayid=target_day.id,
                        time_slot=act.get("timeslot", "morning"),
                        name=act["name"],
                        category=act.get("category", "attraction"),
                        description=act.get("description", ""),
                        latitude=act["coordinates"]["lat"],
                        longitude=act["coordinates"]["lng"],
                        durationminutes=act.get("estimateddurationminutes", 90),
                        estimatedcost=act.get("estimatedcost", 0.0),
                        openinghours=act.get("openinghours"),
                        bookingnotes=act.get("bookingnotes"),
                        sequenceorder=idx,
                        traveltonextjson=act.get("traveltonext")
                    )
                    db.add(new_act)
                db.commit()

        slot_name = op.get("timeslot") or "timeslot"
        target_name = op.get("target") or "removed"
        return {
            "status": "success",
            "intent": "modifytrip",
            "trip": updated_itinerary,
            "answer": f"I have updated Day {op.get('day')} {slot_name} to {target_name}."
        }

    if intent == "plantrip":
        for k, v in cleaned_new_entities.items():
            if v is not None and v != "" and v != []:
                planning_state["entities"][k] = v

        missing = TripPlanningAgent.get_missing_fields(planning_state["entities"])
        if missing:
            question_data = await TripPlanningAgent.handle_conversation(planning_state, cleaned_new_entities, req.message)
            return {
                "status": "needsmoreinfo",
                "intent": "plantrip",
                "missingfields": missing,
                "question": question_data.get("question"),
                "planningstate": planning_state,
                "sessionid": session_id
            }
        else:
            trip_data = await TripPlanningAgent.generate_trip(planning_state["entities"])
            itinerary = trip_data["itinerary"]
            budget_info = trip_data["budget_info"]
            
            trip_id = None
            if current_user:
                new_trip = Trip(
                    userid=current_user.id,
                    destination=planning_state["entities"]["destination"],
                    country=planning_state["entities"]["country"],
                    startdate=datetime.date.fromisoformat(planning_state["entities"]["startdate"]),
                    enddate=datetime.date.fromisoformat(planning_state["entities"]["enddate"]),
                    interests=planning_state["entities"]["interests"],
                    status="completed"
                )
                db.add(new_trip)
                db.commit()
                db.refresh(new_trip)
                trip_id = new_trip.id

                for day in itinerary.get("days", []):
                    new_day = TripDay(
                        tripid=new_trip.id,
                        day_number=day["day"],
                        date=datetime.date.fromisoformat(day["date"]),
                        theme=day.get("theme", ""),
                        estimated_cost=day.get("estimatedcost", 0.0),
                        weatherjson=day.get("weather"),
                        routejson=day.get("route")
                    )
                    db.add(new_day)
                    db.commit()
                    db.refresh(new_day)

                    for idx, act in enumerate(day.get("activities", [])):
                        new_act = Activity(
                            tripdayid=new_day.id,
                            time_slot=act.get("timeslot", "morning"),
                            name=act["name"],
                            category=act.get("category", "attraction"),
                            description=act.get("description", ""),
                            latitude=act["coordinates"]["lat"],
                            longitude=act["coordinates"]["lng"],
                            durationminutes=act.get("estimateddurationminutes", 90),
                            estimatedcost=act.get("estimatedcost", 0.0),
                            openinghours=act.get("openinghours"),
                            bookingnotes=act.get("bookingnotes"),
                            sequenceorder=idx,
                            traveltonextjson=act.get("traveltonext")
                        )
                        db.add(new_act)
                    db.commit()

                new_budget = Budget(
                    tripid=new_trip.id,
                    totalbudget=float(planning_state["entities"]["budget"]),
                    currency=planning_state["entities"]["currency"],
                    total_score=budget_info["score"],
                    comfort_level=budget_info["comfortlevel"],
                    allocationjson=budget_info["allocation"],
                    warningsjson=budget_info["warnings"]
                )
                db.add(new_budget)
                db.commit()

                # Prune older trips
                from .triprouter import prune_old_trips
                prune_old_trips(current_user.id, db)

            return {
                "status": "success",
                "intent": "plantrip",
                "tripid": trip_id,
                "trip": itinerary,
                "budget": budget_info,
                "routesummary": trip_data["route_summary"]
            }

    # Default fallback for travel questions and other unhandled intents
    ans = TravelAssistantAgent.answer(req.message, req.history or [], req.itinerary, intent=intent)
    return {
        "status": "success",
        "intent": "travelquestion",
        "answer": ans
    }

@router.post("/chat-edit")
async def chat_edit(req: ChatEditRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == req.tripid).first()
    if not trip or trip.userid != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this trip.")

    from .triprouter import get_trip_details
    itinerary_details = get_trip_details(trip)

    op = await ItineraryEditor.parse_edit_query(req.message)
    if not op or not op.get("operation"):
        raise HTTPException(status_code=422, detail="Could not parse editing instruction.")

    updated_itinerary = await ItineraryEditor.apply_edit(itinerary_details, op)

    day_num = op.get("day")
    day_idx = int(day_num) - 1
    
    trip_days = sorted(trip.days, key=lambda d: d.day_number)
    target_day = trip_days[day_idx]
    
    db.query(Activity).filter(Activity.tripdayid == target_day.id).delete()
    db.commit()

    updated_day_data = updated_itinerary["days"][day_idx]
    target_day.estimated_cost = updated_day_data.get("estimatedcost", 0.0)
    target_day.routejson = updated_day_data.get("route")
    db.commit()

    for idx, act in enumerate(updated_day_data.get("activities", [])):
        new_act = Activity(
            tripdayid=target_day.id,
            time_slot=act.get("timeslot", "morning"),
            name=act["name"],
            category=act.get("category", "attraction"),
            description=act.get("description", ""),
            latitude=act["coordinates"]["lat"],
            longitude=act["coordinates"]["lng"],
            durationminutes=act.get("estimateddurationminutes", 90),
            estimatedcost=act.get("estimatedcost", 0.0),
            openinghours=act.get("openinghours"),
            bookingnotes=act.get("bookingnotes"),
            sequenceorder=idx,
            traveltonextjson=act.get("traveltonext")
        )
        db.add(new_act)
    db.commit()

    return {
        "status": "success",
        "operation": op,
        "trip": updated_itinerary
    }

@router.post("/update-day")
async def update_day(req: TripUpdateDayRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == req.tripid).first()
    if not trip or trip.userid != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this trip.")

    trip_days = sorted(trip.days, key=lambda d: d.day_number)
    day_idx = req.day - 1
    if day_idx < 0 or day_idx >= len(trip_days):
        raise HTTPException(status_code=404, detail="Day not found.")

    target_day = trip_days[day_idx]

    activities_dict = []
    for act in req.activities:
        activities_dict.append(act.dict())

    optimized_activities = RouteOptimizer.optimize(activities_dict)

    db.query(Activity).filter(Activity.tripdayid == target_day.id).delete()
    db.commit()

    target_day.routejson = [{"lat": act["coordinates"]["lat"], "lng": act["coordinates"]["lng"], "label": act["name"]} for act in optimized_activities]
    target_day.estimated_cost = round(sum([float(act.get("estimatedcost", 0.0)) for act in optimized_activities]), 2)
    db.commit()

    for idx, act in enumerate(optimized_activities):
        new_act = Activity(
            tripdayid=target_day.id,
            time_slot=act.get("timeslot", "morning"),
            name=act["name"],
            category=act.get("category", "attraction"),
            description=act.get("description", ""),
            latitude=act["coordinates"]["lat"],
            longitude=act["coordinates"]["lng"],
            durationminutes=act.get("estimateddurationminutes", 90),
            estimatedcost=act.get("estimatedcost", 0.0),
            openinghours=act.get("openinghours"),
            bookingnotes=act.get("bookingnotes"),
            sequenceorder=idx,
            traveltonextjson=act.get("traveltonext")
        )
        db.add(new_act)
    db.commit()

    total_cost = sum([d.estimated_cost for d in trip.days])
    if trip.budget_info:
        from ..services.budget.budgetscorer import BudgetScorer
        new_score = BudgetScorer.score(trip.budget, trip.currency, len(trip.days), trip.travelercount, trip.destination)
        trip.budget_info.total_score = new_score["score"]
        trip.budget_info.comfort_level = new_score["comfortlevel"]
        trip.budget_info.allocationjson = new_score["allocation"]
        trip.budget_info.warningsjson = new_score["warnings"]
    db.commit()

    from .triprouter import get_trip_details
    return {
        "status": "success",
        "trip": get_trip_details(trip)
    }
