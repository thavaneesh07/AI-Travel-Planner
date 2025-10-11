import json
import random

# Load the existing dataset
with open("backend/nlp/data/sample_queries.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Some simple replacement variations
phrasing_variants = [
    ("Plan a", "Help me plan a"),
    ("Looking for a", "I want a"),
    ("vacation", "trip"),
    ("getaway", "holiday"),
    ("around", "about"),
    ("budget", "cost"),
    ("interested in", "focusing on"),
    ("staying at", "booked in"),
]

def paraphrase(text):
    new_text = text
    # randomly replace some phrases
    for old, new in phrasing_variants:
        if random.random() < 0.4:  # 40% chance to replace
            new_text = new_text.replace(old, new)
    return new_text

# Create augmented dataset
augmented_data = []
for entry in data:
    augmented_data.append(entry)  # keep original
    # make 2 variations
    for _ in range(2):
        new_entry = entry.copy()
        new_entry["query"] = paraphrase(entry["query"])
        augmented_data.append(new_entry)

# Save new file
with open("backend/nlp/data/sample_queries_augmented.json", "w", encoding="utf-8") as f:
    json.dump(augmented_data, f, indent=2, ensure_ascii=False)

print(f"✅ Created {len(augmented_data)} total queries (original + augmented)")
