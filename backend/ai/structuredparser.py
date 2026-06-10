import re
import json
from typing import Dict, Any

def parse_json_safely(raw: str) -> Dict[str, Any]:
    try:
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass
    return {}

def clean_extracted_entities(entities: Dict[str, Any], raw_query: str) -> Dict[str, Any]:
    cleaned = entities.copy()

    # Destination cleanup
    if not cleaned.get("destination"):
        match = re.search(r"\b(?:to|in|for|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", raw_query)
        if match:
            cleaned["destination"] = match.group(1)

    # Budget cleanup
    budget_val = cleaned.get("budget")
    if budget_val is None:
        budget_match = re.search(r"\b(?:budget|around|under|about|~)\s*\$?\s?([\d,]+(?:\.\d+)?)(k)?\b", raw_query.lower())
        if budget_match:
            try:
                num = float(budget_match.group(1).replace(",", ""))
                if budget_match.group(2):
                    num *= 1000
                cleaned["budget"] = int(num)
            except ValueError:
                pass
    else:
        try:
            if isinstance(budget_val, str):
                budget_val = budget_val.lower().replace(",", "").replace("$", "")
                if "k" in budget_val:
                    cleaned["budget"] = int(float(budget_val.replace("k", "")) * 1000)
                else:
                    cleaned["budget"] = int(float(budget_val))
            else:
                cleaned["budget"] = int(budget_val)
        except:
            cleaned["budget"] = None

    # Dates format validation
    for date_field in ("startdate", "enddate"):
        val = cleaned.get(date_field)
        if val:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(val)):
                cleaned[date_field] = None

    # Traveler Count cleanup
    count = cleaned.get("travelercount")
    if count is None:
        match = re.search(r"\b(\d+)\s*(?:people|persons|travelers|friends)\b", raw_query.lower())
        if match:
            cleaned["travelercount"] = int(match.group(1))
    else:
        try:
            cleaned["travelercount"] = int(count)
        except:
            cleaned["travelercount"] = 1

    # Traveler Type cleanup
    t_type = cleaned.get("travelertype")
    if not t_type:
        for p in ("solo", "couple", "family", "group"):
            if p in raw_query.lower():
                cleaned["travelertype"] = p
                break
    
    if cleaned.get("travelertype") not in ("solo", "couple", "family", "group"):
        cleaned["travelertype"] = "solo"

    # Currency extraction and normalization
    curr_raw = cleaned.get("currency")
    if curr_raw:
        curr_upper = str(curr_raw).upper().strip()
        if curr_upper in ("$", "USD", "DOLLAR", "DOLLARS"):
            cleaned["currency"] = "USD"
        elif curr_upper in ("€", "EUR", "EURO", "EUROS"):
            cleaned["currency"] = "EUR"
        elif curr_upper in ("£", "GBP", "POUND", "POUNDS"):
            cleaned["currency"] = "GBP"
        elif curr_upper in ("₹", "INR", "RUPEE", "RUPEES"):
            cleaned["currency"] = "INR"
        elif curr_upper in ("¥", "JPY", "YEN"):
            cleaned["currency"] = "JPY"
        elif len(curr_upper) == 3 and curr_upper.isalpha():
            cleaned["currency"] = curr_upper
        else:
            cleaned["currency"] = "USD"
    else:
        # Check raw query for symbols/names
        if "eur" in raw_query.lower() or "€" in raw_query:
            cleaned["currency"] = "EUR"
        elif "gbp" in raw_query.lower() or "£" in raw_query:
            cleaned["currency"] = "GBP"
        elif "₹" in raw_query or "inr" in raw_query.lower() or "rupee" in raw_query.lower():
            cleaned["currency"] = "INR"
        elif "¥" in raw_query or "jpy" in raw_query.lower() or "yen" in raw_query.lower():
            cleaned["currency"] = "JPY"
        elif "aud" in raw_query.lower():
            cleaned["currency"] = "AUD"
        elif "cad" in raw_query.lower():
            cleaned["currency"] = "CAD"
        elif "sgd" in raw_query.lower():
            cleaned["currency"] = "SGD"
        elif "chf" in raw_query.lower():
            cleaned["currency"] = "CHF"
        else:
            # Match any 3-letter currency code or default to USD
            currency_match = re.search(r"\b([A-Za-z]{3})\b", raw_query)
            if currency_match:
                code = currency_match.group(1).upper()
                # Exclude common non-currency 3-letter words
                EXCLUDE_WORDS = {"THE", "AND", "FOR", "YOU", "BUT", "ARE", "NOT", "DAY", "OUT", "GET", "WAS", "NEW", "HOW", "WHO", "WHO", "OUR", "ITS", "HAS", "HAD"}
                if code not in EXCLUDE_WORDS:
                    cleaned["currency"] = code
                else:
                    cleaned["currency"] = "USD"
            else:
                cleaned["currency"] = "USD"

    return cleaned
