# backend/nlp/nlp_parser.py
import re
import datetime
import calendar
import spacy
from difflib import get_close_matches
from dateparser.search import search_dates

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def _strip_budget_like_text(q: str) -> str:
    """
    Remove budget/money tokens to avoid interfering with date parsing.
    Examples: '$1200', '15k', '~2,500', 'about 3k', 'under 5,000'
    """
    q = re.sub(r"\$\s*[\d,]+(?:\.\d+)?", " ", q)                        # $1200, $1,200.50
    q = re.sub(r"\b[\d,]+(?:\.\d+)?\s*k\b", " ", q, flags=re.IGNORECASE) # 2.5k, 15k
    q = re.sub(r"\b(?:budget|around|under|approx\.?|about|~|cost|price|of|with)\b", " ", q, flags=re.IGNORECASE)
    return q

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# --- Constants ---
MONTHS = {
    "january","february","march","april","may","june","july","august",
    "september","october","november","december",
    "jan","feb","mar","apr","may","jun","jul","aug","sep","sept","oct","nov","dec"
}
STOP_WORDS = {"next", "this", "coming", "week", "month", "year", "from", "between", "to", "and", "on", "in", "during"}
RELATIVE_DATE_WORDS = {
    "today", "tomorrow", "tonight", "week", "weekend", "month", "year",
    "monday","tuesday","wednesday","thursday","friday","saturday","sunday",
    "next","coming"
}

# ==========================================================
# DESTINATION EXTRACTION
# ==========================================================
def extract_destination(doc):
    """Extract destination from user query."""
    candidate = []
    started = False
    for token in doc:
        if token.lower_ in ["to", "in", "for"]:
            started = True
            continue
        if started:
            if (
                token.pos_ in ["PROPN", "NOUN"]
                and token.lower_ not in MONTHS
                and token.lower_ not in STOP_WORDS
                and token.lower_ not in RELATIVE_DATE_WORDS
            ):
                candidate.append(token.text)
            elif token.lower_ == "the":  # allow "the Maldives"
                continue
            else:
                break
    if candidate:
        return " ".join(candidate)
    # fallback: longest GPE/LOC entity
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    return max(locations, key=len) if locations else None

# ==========================================================
# DATE EXTRACTION
# ==========================================================
def extract_dates(query: str):
    today = datetime.date.today()
    settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.datetime.now()}
    ql = query.lower()

    start_date, end_date = None, None

    # --- Relative phrases ---
    if "tomorrow" in ql:
        s = today + datetime.timedelta(days=1)
        return s.strftime("%Y-%m-%d"), s.strftime("%Y-%m-%d"), 1
    if "day after tomorrow" in ql:
        s = today + datetime.timedelta(days=2)
        return s.strftime("%Y-%m-%d"), s.strftime("%Y-%m-%d"), 1
    if "next week" in ql:
        start = today + datetime.timedelta(days=(7 - today.weekday()))
        end = start + datetime.timedelta(days=6)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), 7
    if "next weekend" in ql:
        days_ahead = (5 - today.weekday()) % 7
        start = today + datetime.timedelta(days=days_ahead)
        end = start + datetime.timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), 2

    # --- Explicit ranges: "May 5-10 2025" ---
    range_match = re.search(r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s*[-–]\s*(\d{1,2})(?:,?\s*(\d{4}))?", query)
    if range_match:
        month, start_day, end_day, year = range_match.groups()
        year = year or str(today.year)
        try:
            start_date = datetime.datetime.strptime(f"{month} {start_day} {year}", "%B %d %Y").date()
        except ValueError:
            start_date = datetime.datetime.strptime(f"{month} {start_day} {year}", "%b %d %Y").date()
        end_date = datetime.date(start_date.year, start_date.month, int(end_day))

    # --- "from X to Y" or "between X and Y" ---
    if not start_date:
        range_pattern = r"(?:from|between)\s+(.*?)\s+(?:to|and)\s+(.*?)(?:,|$)"
        match = re.search(range_pattern, query, re.IGNORECASE)
        if match:
            left, right = match.groups()
            parsed_left = search_dates(left, settings=settings)
            parsed_right = search_dates(right, settings=settings)
            if parsed_left and parsed_right:
                start_date = parsed_left[0][1].date()
                end_date = parsed_right[0][1].date()
                # Align year if necessary
                if start_date.year != end_date.year and (abs((end_date - start_date).days) > 180):
                    start_date = start_date.replace(year=end_date.year)

    # --- Month-only phrases ---
    if not start_date:
        for m in range(1, 13):
            month_name = datetime.date(2000, m, 1).strftime("%B").lower()
            if month_name in ql:
                year = today.year if m >= today.month else today.year + 1
                start_date = datetime.date(year, m, 1)
                last_day = calendar.monthrange(year, m)[1]
                end_date = datetime.date(year, m, last_day)
                break

    # --- Fallback: dateparser ---
    if not start_date:
        cleaned_query = _strip_budget_like_text(query)
        parsed = search_dates(cleaned_query, settings=settings)
        if parsed:
            start_date = parsed[0][1].date()
            if len(parsed) > 1:
                end_date = parsed[-1][1].date()

    # --- Normalize dates ---
    if start_date:
        if not end_date:
            end_date = start_date + datetime.timedelta(days=3)
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        explicit_year = bool(re.search(r"\b\d{4}\b", query))
        if not explicit_year and end_date < today:
            start_date = start_date.replace(year=start_date.year + 1)
            end_date = end_date.replace(year=end_date.year + 1)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        trip_duration = (datetime.datetime.strptime(end_date, "%Y-%m-%d") -
                         datetime.datetime.strptime(start_date, "%Y-%m-%d")).days + 1
        return start_date, end_date, trip_duration

    return None, None, None

# ==========================================================
# GROUP SIZE EXTRACTION
# ==========================================================
def extract_group_size(query: str, profile: str):
    # Try explicit numbers like "5 friends" or "family of 6"
    match = re.search(r"(\d+)\s+(?:friends|people|persons|members)", query.lower())
    if match:
        return int(match.group(1))
    if profile == "family":
        match = re.search(r"family of (\d+)", query.lower())
        if match:
            return int(match.group(1))
    # Fallback: default from profile
    profiles = {"solo": 1, "couple": 2, "family": 4, "friends": 3}
    return profiles.get(profile, 1)

# ==========================================================
# MAIN PARSER FUNCTION
# ==========================================================
def parse_user_query(query: str):
    doc = nlp(query)
    query_lower = query.lower()

    # Destination
    destination = extract_destination(doc)

    # Dates
    start_date, end_date, trip_duration = extract_dates(query)

    # Budget
    budget_match = re.search(
        r"(?:budget|around|under|approx\.?|cost|about|price|of|with|~)\s*\$?\s?([\d,]+(?:\.\d+)?)(k)?",
        query_lower
    )
    budget = None
    if budget_match:
        num_str = budget_match.group(1).replace(",", "")
        try:
            num = float(num_str)
            if budget_match.group(2):  # 'k'
                num *= 1000
            budget = int(num)
        except ValueError:
            pass

    # Profile + group size
    profiles = {"solo": 1, "couple": 2, "family": 4, "friends": 3}
    profile = None
    for p in profiles.keys():
        if p in query_lower:
            profile = p
            break
    group_size = extract_group_size(query, profile)

    # Accommodation
    accommodations = ["hotel", "airbnb", "hostel", "resort", "villa", "apartment", "homestay"]
    accommodation = next((a for a in accommodations if a in query_lower), None)

    # Interests
    interest_keywords = [
        "food", "art", "history", "adventure", "shopping", "beaches",
        "hiking", "culture", "nightlife", "photography", "relaxation", "wildlife"
    ]
    interests = [i for i in interest_keywords if re.search(rf"\b{i}\b", query_lower)]

    # Synonym map
    synonyms = {
        "foodie": "food",
        "art lover": "art",
        "party": "nightlife",
        "hiker": "hiking",
        "beach": "beaches"
    }
    for syn, canonical in synonyms.items():
        if syn in query_lower and canonical not in interests:
            interests.append(canonical)

    # Fuzzy match
    for word in query_lower.split():
        match = get_close_matches(word, interest_keywords, n=1, cutoff=0.8)
        if match and match[0] not in interests:
            interests.append(match[0])

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "trip_duration": trip_duration,
        "budget": budget,
        "user_profile": profile,
        "group_size": group_size,
        "accommodation": accommodation,
        "interests": interests,
    }

# ==========================================================
# TESTING
# ==========================================================
if __name__ == "__main__":
    test_queries = [
        "Trip to Paris Oct 1-7 2025, budget 1500, solo, history and food",
        "Vacation in Goa in December, budget 20000, family trip",
        "Plan for Maldives from June 3 to June 8, budget 2500",
        "Solo trip to Bali next week, budget $800",
        "Couple trip between July 10 and July 15 to Switzerland, budget 5000, adventure and photography",
        "Friends trip to New York City in March, budget 3500, nightlife and food",
        "Trip to Tokyo October 1-7 2025, budget 5k, couple",
        "Family holiday in Dubai in November, around 3000 USD",
        "Plan a trip to Rome from 5th May to 10th May 2025 with a budget of 2500",
        "Couple vacation in Sydney between 2nd April and 6th April 2025, cost 2000 dollars"
    ]

    for q in test_queries:
        print(f"\n🔍 Query: {q}")
        print(parse_user_query(q))
