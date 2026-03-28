# Initial filtering

import re
from ml_engine import get_ml_risk_score
from llm_judge import get_llm_risk_score

# Basic suspicious patterns
PATTERNS = [
    r"ignore previous instructions",
    r"reveal (the )?system prompt",
    r"act as (dan|developer mode)",
    r"bypass (security|filters)",
]

KEYWORDS = {
    "ignore": 0.1,
    "bypass": 0.25,
    "reveal": 0.2,
    "system prompt": 0.4,
}

def scan_prompt(prompt: str):
    prompt_lower = prompt.lower()
    flags = []
    rule_score = 0.0
    
# ==============================================================
    # Rules Layer
    
    # Regex pattern matching
    for pattern in PATTERNS:
        if re.search(pattern, prompt_lower):
            flags.append(f"pattern:{pattern}")
            rule_score += 0.4

    # Keyword spotting
    for word, weight in KEYWORDS.items():
        if word in prompt_lower:
            flags.append(f"keyword:{word}")
            rule_score += weight

    # Token-anomaly scoring
    if len(prompt) > 500:
        flags.append("long_prompt")
        rule_score += 0.2

    # Clamp score to 1.0
    rule_score = min(rule_score, 1.0)

# ==============================================================
    # Machine Learning Layer
    
    ml_score = get_ml_risk_score(prompt)
    if ml_score > 0.6:
        flags.append("ml_injection_detected")
        
# ==============================================================

    # 3. Contextual Risk Scoring Layer (LLM Judge)
    llm_score = get_llm_risk_score(prompt)
    if llm_score > 0.7:
        flags.append("llm_judge_flagged")

# ==============================================================

    # Final Aggregate Score
    final_score = (0.25 * rule_score) + (0.5 * ml_score) + (0.25 * llm_score)
    
    # If rule or ML layers have a high certainty score but LLM judge doesn't for some reason
    # Forces a block due to high certainty from one of two sources
    if rule_score >= 0.9 or ml_score >= 0.95:
        final_score = max(final_score, 0.9)

    return {
        "score": round(final_score, 3),
        "flags": flags,
        "breakdown": {
            "rule_score": round(rule_score, 3),
            "ml_score": round(ml_score, 3),
            "llm_score": round(llm_score, 3)
        }
    }