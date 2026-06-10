import re
from dateparser.search import search_dates
import datetime

def _strip_budget_like_text(q: str) -> str:
    # Remove phrases like "budget 1500"
    q = re.sub(
        r"\b(?:budget|around|under|approx\.?|about|~|cost|price|of|with|limit)\s*\$?\s*[\d,]+(?:\s*(?:usd|dollars|pounds|euros|k))?\b",
        " ",
        q,
        flags=re.IGNORECASE
    )
    # Remove standalone $1200
    q = re.sub(r"\$\s*[\d,]+(?:\.\d+)?", " ", q)
    # Remove standalone 15k
    q = re.sub(r"\b[\d,]+(?:\.\d+)?\s*k\b", " ", q, flags=re.IGNORECASE)
    # Remove leftover budget keywords
    q = re.sub(r"\b(?:budget|around|under|approx\.?|about|~|cost|price|of|with)\b", " ", q, flags=re.IGNORECASE)
    return q

def extract_dates(query: str):
    today = datetime.date.today()
    settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.datetime.now()}
    
    q_no_budget = _strip_budget_like_text(query)
    start_date, end_date = None, None
    duration_days = None

    # Fallback: dateparser
    cleaned_query = _strip_budget_like_text(query)
    parsed = search_dates(cleaned_query, settings=settings)
    if parsed:
        start_date = parsed[0][1].date()
        if len(parsed) > 1:
            end_date = parsed[-1][1].date()

    # --- Normalize dates ---
    if start_date:
        if end_date and start_date.year != end_date.year and abs((end_date - start_date).days) > 180:
            year_match = re.search(r"\b(20\d{2})\b", query)
            if year_match:
                year = int(year_match.group(1))
                start_date = start_date.replace(year=year)
                end_date = end_date.replace(year=year)
            else:
                start_date = start_date.replace(year=end_date.year)

        if not end_date:
            end_date = start_date + datetime.timedelta(days=(duration_days - 1) if duration_days else 3)
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        trip_duration = (end_date - start_date).days + 1
        return start_date_str, end_date_str, trip_duration

    return None, None, None

query = "Plan a trip to Paris Oct 1 to Oct 7 2025, budget 1500, solo, history/food"
s, e, d = extract_dates(query)
print("Parsed Start Date:", s)
print("Parsed End Date:", e)
print("Parsed Duration:", d)
