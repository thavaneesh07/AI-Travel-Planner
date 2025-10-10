# backend/nlp/nlp_parser.py
import re
import datetime
import spacy
from dateparser.search import search_dates

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

MONTHS = set([
    "january","february","march","april","may","june","july","august",
    "september","october","november","december",
    "jan","feb","mar","apr","may","jun","jul","aug","sep","sept","oct","nov","dec"
])

STOP_WORDS = set(["next", "this", "coming", "week", "month", "year", "from", "between", "to", "and", "on", "in", "during"])

def extract_destination(doc):
    """
    Extract destination from the SpaCy doc.
    Prefer multi-word proper nouns (e.g., New York City).
    Stop when hitting month names, digits, or relative phrases.
    """
    candidate = []
    started = False
    for token in doc:
        if token.lower_ in ["to", "in", "for"]:
            started = True
            continue
        if started:
            if token.pos_ == "PROPN" and token.lower_ not in MONTHS and token.lower_ not in STOP_WORDS:
                candidate.append(token.text)
            else:
                break
    if candidate:
        return " ".join(candidate)
    # fallback: longest GPE/LOC
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    if locations:
        return max(locations, key=len)
    return None

def extract_dates(query: str):
    """
    Extract start_date and end_date as 'YYYY-MM-DD' strings.
    Handles ranges, month-only phrases, relative dates, and hyphenated day ranges.
    """
    today = datetime.date.today()
    settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.datetime.now()}

    # 1️⃣ Hyphenated ranges like "Oct 1-7 2025" or "October 1-7 2025"
    hyphen_range = re.search(r"([A-Za-z]+ \d{1,2})-(\d{1,2}) (\d{4})", query)
    if hyphen_range:
        start_str, end_day, year = hyphen_range.groups()
        try:
            start_date = datetime.datetime.strptime(f"{start_str} {year}", "%b %d %Y").date()
        except ValueError:
            start_date = datetime.datetime.strptime(f"{start_str} {year}", "%B %d %Y").date()
        end_date = datetime.date(int(year), start_date.month, int(end_day))
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # 2️⃣ 'from X to Y' or 'between X and Y'
    range_pattern = r"(?:from|between)\s+(.*?)\s+(?:to|and)\s+(.*?)(?:,|$)"
    range_match = re.search(range_pattern, query, re.IGNORECASE)
    if range_match:
        left, right = range_match.groups()
        parsed_left = search_dates(left, settings=settings)
        parsed_right = search_dates(right, settings=settings)
        if parsed_left and parsed_right:
            s = parsed_left[0][1].date()
            e = parsed_right[0][1].date()
            if s < today:
                try:
                    s = s.replace(year=today.year + 1)
                    e = e.replace(year=today.year + 1)
                except ValueError:
                    pass
            return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")

    # 3️⃣ Month-only phrases like "in December" or "December trip"
    month_match = None
    for m in MONTHS:
        if re.search(rf"\b{m}\b", query.lower()):
            month_match = m
            break
    if month_match:
        try:
            month_num = datetime.datetime.strptime(month_match, "%B").month
        except ValueError:
            month_num = datetime.datetime.strptime(month_match, "%b").month
        year = today.year
        if month_num < today.month:
            year += 1
        start_date = datetime.date(year, month_num, 1)
        if month_num < 12:
            end_date = datetime.date(year, month_num + 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, 12, 31)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    # 4️⃣ Fallback: search_dates for relative phrases
    parsed = search_dates(query, settings=settings)
    if parsed:
        s = parsed[0][1].date()
        e = parsed[-1][1].date() if len(parsed) > 1 else None
        if s < today:
            try:
                s = s.replace(year=today.year + 1)
                if e:
                    e = e.replace(year=today.year + 1)
            except ValueError:
                pass
        return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d") if e else None

    return None, None

def parse_user_query(query: str):
    doc = nlp(query)
    query_lower = query.lower()

    # 1️⃣ Destination
    destination = extract_destination(doc)

    # 2️⃣ Dates
    start_date, end_date = extract_dates(query)

    # 3️⃣ Budget (anchored to keywords to avoid picking up years)
    budget_match = re.search(
        r"(?:budget|around|under|approx\.?)\s*\$?\s?(\d+)(k)?",
        query_lower
    )
    budget = None
    if budget_match:
        num = int(budget_match.group(1))
        if budget_match.group(2):  # has 'k'
            num *= 1000
        budget = num

    # 4️⃣ Profile
    profiles = ["solo", "couple", "family", "friends"]
    profile = next((p for p in profiles if p in query_lower), None)

    # 5️⃣ Interests
    interest_keywords = [
        "food", "art", "history", "adventure", "shopping", "beaches",
        "hiking", "culture", "nightlife", "photography", "relaxation", "wildlife"
    ]
    interests = [i for i in interest_keywords if re.search(rf"\b{i}\b", query_lower)]

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "user_profile": profile,
        "interests": interests,
    }

if __name__ == "__main__":
    test_queries = [
        "Trip to Paris Oct 1-7 2025, budget 1500, solo, history and food",
        "Vacation in Goa in December, budget 20000, family trip",
        "Plan for Maldives from June 3 to June 8, budget 2500",
        "Solo trip to Bali next week, budget $800",
        "Couple trip between July 10 and July 15 to Switzerland, budget 5000, adventure and photography",
        "Friends trip to New York City in March, budget 3500, nightlife and food",
        "Trip to Tokyo October 1-7 2025, budget 5k, couple"
    ]

    for q in test_queries:
        print(f"\n🔍 Query: {q}")
        print(parse_user_query(q))