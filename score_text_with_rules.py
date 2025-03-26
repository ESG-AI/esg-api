import json
import re

# Load scoring rules from JSON once
with open("scoring_rules.json", "r", encoding="utf-8") as f:
    scoring_rules = json.load(f)

def score_text_with_rules(extracted_text: str):
    results = {
        "total_score": 0,
        "indicators": []
    }

    # Normalize text for matching
    text_lower = extracted_text.lower()

    for gri_code, rule in scoring_rules.items():
        indicator_result = {
            "GRI": gri_code,
            "description": rule.get("description", ""),
            "found_keywords": [],
            "score": 0,
            "criteria_explanation": rule.get("criteria", {})
        }

        # Check for keyword matches
        found = False
        keyword_hits = []
        for keyword in rule["keywords"]:
            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
            if re.search(pattern, text_lower):
                keyword_hits.append(keyword)
                found = True

        indicator_result["found_keywords"] = keyword_hits

        # Simple scoring logic (initial version):
        if found:
            # Assign a provisional score — 
            # This could be: min(1 + 0.5 * number_of_hits, 4) or just 2 by default
            indicator_result["score"] = min(4, 1 + int(len(keyword_hits) / 2))
        else:
            indicator_result["score"] = 0

        results["indicators"].append(indicator_result)

    # Calculate total score by summing all
    results["total_score"] = sum([i["score"] for i in results["indicators"]])

    return results
