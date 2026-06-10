import json
import re
from typing import Dict, Any, List
from .ollamaclient import OllamaClient
from .promptregistry import PROMPTS

SUPPORTEDINTENTS = [
    "travelquestion",
    "destinationrecommendation",
    "plantrip",
    "modifytrip",
    "weatherquery",
    "visaquery",
    "budgetquery",
    "hotelsearch",
    "flightsearch",
    "itinerarygeneration"
]

REQUIREDTRIPFIELDS = [
    "destination",
    "country",
    "startdate",
    "enddate",
    "travelercount",
    "travelertype",
    "budget",
    "currency",
    "interests"
]

COUNTRIES = {
    "afghanistan", "albania", "algeria", "andorra", "angola", "antigua and barbuda", "argentina", "armenia", "australia", "austria", "azerbaijan",
    "bahamas", "bahrain", "bangladesh", "barbados", "belarus", "belgium", "belize", "benin", "bhutan", "bolivia", "bosnia and herzegovina", "botswana", "brazil", "brunei", "bulgaria", "burkina faso", "burundi",
    "cabo verde", "cambodia", "cameroon", "canada", "central african republic", "chad", "chile", "china", "colombia", "comoros", "congo", "costa rica", "croatia", "cuba", "cyprus", "czechia", "czech republic",
    "denmark", "djibouti", "dominica", "dominican republic",
    "east timor", "ecuador", "egypt", "el salvador", "equatorial guinea", "eritrea", "estonia", "eswatini", "ethiopia",
    "fiji", "finland", "france",
    "gabon", "gambia", "georgia", "germany", "ghana", "greece", "grenada", "guatemala", "guinea", "guinea-bissau", "guyana",
    "haiti", "honduras", "hungary",
    "iceland", "india", "indonesia", "iran", "iraq", "ireland", "israel", "italy", "ivory coast",
    "jamaica", "japan", "jordan",
    "kazakhstan", "kenya", "kiribati", "kosovo", "kuwait", "kyrgyzstan",
    "laos", "latvia", "lebanon", "lesotho", "liberia", "libya", "liechtenstein", "lithuania", "luxembourg",
    "madagascar", "malawi", "malaysia", "maldives", "mali", "malta", "marshall islands", "mauritania", "mauritius", "mexico", "micronesia", "moldova", "monaco", "mongolia", "montenegro", "morocco", "mozambique", "myanmar",
    "namibia", "nauru", "nepal", "netherlands", "new zealand", "nicaragua", "niger", "nigeria", "north korea", "north macedonia", "norway",
    "oman",
    "pakistan", "palau", "panama", "papua new guinea", "paraguay", "peru", "philippines", "poland", "portugal",
    "qatar",
    "romania", "russia", "rwanda",
    "saint kitts and nevis", "saint lucia", "saint vincent and the grenadines", "samoa", "san marino", "sao tome and principe", "saudi arabia", "senegal", "serbia", "seychelles", "sierra leone", "singapore", "slovakia", "slovenia", "solomon islands", "somalia", "south africa", "south korea", "south sudan", "spain", "sri lanka", "sudan", "suriname", "sweden", "switzerland", "syria",
    "taiwan", "tajikistan", "tanzania", "thailand", "togo", "tonga", "trinidad and tobago", "tunisia", "turkey", "turkmenistan", "tuvalu",
    "uganda", "ukraine", "united arab emirates", "uae", "united kingdom", "uk", "united states", "usa", "us", "uruguay", "uzbekistan",
    "vanuatu", "vatican city", "venezuela", "vietnam",
    "yemen",
    "zambia", "zimbabwe"
}

class TravelIntentEngine:
    @staticmethod
    def analyze(message: str, current_state: Dict[str, Any] = None) -> Dict[str, Any]:
        current_state = current_state or {}
        
        # 1. Intent Detection
        intent_prompt = PROMPTS["intentdetection"].format(
            current_state=json.dumps(current_state),
            message=message
        )
        intent_res = OllamaClient.call_ollama(intent_prompt)
        
        intent = "travelquestion"
        confidence = 0.5
        
        try:
            m = re.search(r"\{.*\}", intent_res, re.S)
            if m:
                data = json.loads(m.group(0))
                intent = data.get("intent", "travelquestion")
                confidence = float(data.get("confidence", 0.5))
        except Exception:
            pass

        # Validate against supported intents
        if intent not in SUPPORTEDINTENTS and intent != "nontravel":
            intent = "travelquestion"

        # Fallback to rule-based classification if Ollama returned nothing or couldn't parse
        if not intent_res or intent == "travelquestion":
            message_lower = message.lower()
            
            from ..nlp.nlp_parser import parse_user_query
            parsed = parse_user_query(message)
            
            if any(w in message_lower for w in ["weather", "temperature", "forecast", "rain", "sunny", "climate", "snow", "season"]):
                intent = "weatherquery"
                confidence = 0.9
            elif any(w in message_lower for w in ["visa", "passport", "entry requirement", "documents", "entry requirements"]):
                intent = "visaquery"
                confidence = 0.9
            elif any(w in message_lower for w in ["expensive", "cheap", "cost of living", "prices", "cost of a", "budget for"]) and not any(k in message_lower for k in ["plan", "itinerary", "generate"]):
                intent = "budgetquery"
                confidence = 0.9
            elif any(w in message_lower for w in ["best time", "when to visit", "when is the best", "safety", "safe for", "currency", "food destination", "food destinations", "should i travel", "where should i travel"]):
                intent = "travelquestion"
                confidence = 0.9
            elif message_lower.startswith(("what", "where", "how", "when", "why", "is", "are", "should", "can", "do", "does")) or "?" in message_lower:
                plan_verbs = ["plan", "itinerary", "generate", "create", "make"]
                if not any(v in message_lower for v in plan_verbs):
                    intent = "travelquestion"
                    confidence = 0.9
                else:
                    intent = "plantrip"
                    confidence = 0.9
            else:
                plan_keywords = ["plan", "trip", "itinerary", "vacation", "travel to", "go to", "visit", "schedule", "tour", "book", "generate", "create"]
                is_plan = any(k in message_lower for k in plan_keywords)
                if is_plan or parsed.get("start_date") or parsed.get("budget"):
                    intent = "plantrip"
                    confidence = 0.9
                else:
                    intent = "travelquestion"
                    confidence = 0.5

        # 2. Entity Extraction
        entities = {
            "destination": None,
            "country": None,
            "startdate": None,
            "enddate": None,
            "budget": None,
            "currency": None,
            "travelercount": None,
            "travelertype": None,
            "interests": []
        }
        
        is_planning_session = False
        if current_state and current_state.get("entities", {}).get("destination"):
            missing_fields = []
            for field in REQUIREDTRIPFIELDS:
                if not current_state["entities"].get(field):
                    missing_fields.append(field)
            if missing_fields:
                is_planning_session = True

        if intent in ("plantrip", "modifytrip", "itinerarygeneration") or is_planning_session:
            extracted_successfully = False
            from ..config import settings
            if settings.USE_OLLAMA:
                extract_prompt = PROMPTS["entityextraction"].format(message=message)
                extract_res = OllamaClient.call_ollama(extract_prompt)
                try:
                    m = re.search(r"\{.*\}", extract_res, re.S)
                    if m:
                        extracted_data = json.loads(m.group(0))
                        for k in entities.keys():
                            val = extracted_data.get(k)
                            if val is not None and val != "":
                                entities[k] = val
                        extracted_successfully = True
                except Exception:
                    pass

            # Use rule-based entity extraction as a fallback or addition
            from ..nlp.nlp_parser import parse_user_query
            parsed = parse_user_query(message)


            
            # Rule-based country check on clean message
            msg_clean = re.sub(r"[^\w\s]", "", message).strip().lower()
            if msg_clean in COUNTRIES:
                entities["country"] = message.strip().strip(".,!").title()

            if parsed.get("destination"):
                dest_val = parsed["destination"]
                dest_lower = dest_val.lower()
                if dest_lower in COUNTRIES:
                    if not entities.get("country"):
                        entities["country"] = dest_val.title()
                    # Only set destination if it's not set in entities and not set in current state
                    if not entities.get("destination") and not (current_state and current_state.get("entities", {}).get("destination")):
                        entities["destination"] = dest_val
                else:
                    if not entities.get("destination"):
                        entities["destination"] = dest_val

            if parsed.get("start_date") and not entities.get("startdate"):
                entities["startdate"] = parsed["start_date"]
            if parsed.get("end_date") and not entities.get("enddate"):
                entities["enddate"] = parsed["end_date"]
            if parsed.get("budget") and not entities.get("budget"):
                entities["budget"] = parsed["budget"]
            if parsed.get("user_profile") and not entities.get("travelertype"):
                entities["travelertype"] = parsed["user_profile"]
            if parsed.get("group_size") and not entities.get("travelercount"):
                entities["travelercount"] = parsed["group_size"]
            if parsed.get("interests") and not entities.get("interests"):
                entities["interests"] = parsed["interests"]

            # Infer country if destination is known
            if entities.get("destination") and not entities.get("country"):
                country_mapping = {
                    "paris": "France",
                    "tokyo": "Japan",
                    "london": "United Kingdom",
                    "new york": "United States",
                    "nyc": "United States",
                    "bali": "Indonesia",
                    "rome": "Italy",
                    "barcelona": "Spain",
                    "swiss": "Switzerland",
                    "switzerland": "Switzerland",
                    "sydney": "Australia",
                    "dubai": "United Arab Emirates",
                    "goa": "India",
                    "delhi": "India",
                    "mumbai": "India",
                    "bangkok": "Thailand",
                    "singapore": "Singapore",
                }
                dest_lower = entities["destination"].lower()
                for city, country_name in country_mapping.items():
                    if city in dest_lower:
                        entities["country"] = country_name
                        break
            
            # Do not default currency here; let clean_extracted_entities handle fallback.
            pass

        # Post-process entities: if destination is a country, and session already has a destination,
        # treat the extracted destination as the country instead.
        if entities.get("destination"):
            dest_lower = entities["destination"].lower()
            if dest_lower in COUNTRIES:
                if not entities.get("country"):
                    entities["country"] = entities["destination"]
                # If current state already has a destination, clear the extracted destination to prevent overwriting
                if current_state and current_state.get("entities", {}).get("destination"):
                    entities["destination"] = None

        # Merge entities with current state to figure out what's missing
        merged_entities = current_state.get("entities", {}).copy() if current_state else {}
        for k, v in entities.items():
            if v is not None and v != "" and v != []:
                merged_entities[k] = v

        # Calculate missing required fields
        missing_fields = []
        for field in REQUIREDTRIPFIELDS:
            if not merged_entities.get(field):
                missing_fields.append(field)

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "missingfields": missing_fields
        }
