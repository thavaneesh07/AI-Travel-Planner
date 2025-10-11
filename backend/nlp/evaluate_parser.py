import json
from datetime import datetime
from nlp_parser import parse_user_query

# --- Load Dataset ---
with open("backend/nlp/data/sample_queries_augmented.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Fields to evaluate ---
fields = [
    "destination",
    "start_date",
    "end_date",
    "trip_duration",
    "budget",
    "user_profile",
    "group_size",
    "accommodation",
    "interests",
]

# --- Initialize counters ---
scores = {f: {"correct": 0, "total": 0} for f in fields}

# --- Helper functions ---
def dates_close(d1, d2, delta_days=1):
    """Return True if two date strings are within ±delta_days."""
    try:
        dt1 = datetime.strptime(d1, "%Y-%m-%d")
        dt2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((dt1 - dt2).days) <= delta_days
    except Exception:
        return False

def numbers_close(n1, n2, tolerance=1):
    """Return True if two numbers are within ±tolerance."""
    try:
        return abs(int(n1) - int(n2)) <= tolerance
    except Exception:
        return False

def lists_match(pred_list, true_list):
    """Return True if two lists have any overlap."""
    return bool(set(pred_list) & set(true_list))

# --- Evaluation loop ---
for entry in data:
    query = entry["query"]
    expected = entry["output"]
    predicted = parse_user_query(query)

    for f in fields:
        scores[f]["total"] += 1
        exp_val = expected.get(f)
        pred_val = predicted.get(f)

        if exp_val is None or pred_val is None:
            continue

        # --- Special handling per field ---
        if f == "interests":
            if lists_match(pred_val, exp_val):
                scores[f]["correct"] += 1

        elif f in ["start_date", "end_date"]:
            if dates_close(pred_val, exp_val):
                scores[f]["correct"] += 1

        elif f in ["trip_duration", "group_size", "budget"]:
            if numbers_close(pred_val, exp_val):
                scores[f]["correct"] += 1

        elif isinstance(exp_val, str) and isinstance(pred_val, str):
            if exp_val.lower().strip() == pred_val.lower().strip():
                scores[f]["correct"] += 1

        else:
            if exp_val == pred_val:
                scores[f]["correct"] += 1

# --- Print accuracy per field ---
print("\n🔍 Parser Evaluation Results:")
for f in fields:
    total = scores[f]["total"]
    correct = scores[f]["correct"]
    accuracy = (correct / total) * 100 if total else 0
    print(f"{f:15}: {accuracy:.2f}% ({correct}/{total})")

# --- Overall accuracy ---
overall_acc = (
    sum(s["correct"] for s in scores.values())
    / sum(s["total"] for s in scores.values())
    * 100
)
print(f"\n🌍 Overall Accuracy: {overall_acc:.2f}%")
