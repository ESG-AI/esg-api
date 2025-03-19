import json
import re
from collections import defaultdict

# Load scoring rules from JSON
with open("scoring_rules.json", "r") as f:
    scoring_rules = json.load(f)

def score_text(text: str) -> dict:
    """
    Score extracted text based on scoring_rules.json.
    Returns ESG pillar breakdown, total score, and indicator presence.
    """
    text_lower = text.lower()
    pillar_scores = defaultdict(int)
    indicator_results = []

    for gri_code, rule in scoring_rules.items():
        found = False

        # Check if any keyword is present in the text
        for keyword in rule["keywords"]:
            if re.search(rf'\b{re.escape(keyword.lower())}\b', text_lower):
                found = True
                break

        score = rule["weight"] if found else 0
        pillar_scores[rule.get("pillar", "Unknown")] += score

        indicator_results.append({
            "GRI": gri_code,
            "description": rule["description"],
            "found": found,
            "score": score
        })

    total_score = sum(pillar_scores.values())

    return {
        "score_breakdown": pillar_scores,
        "total_score": total_score,
        "indicators": indicator_results
    }
