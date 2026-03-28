# Define what we do with the given prompt

def decide_action(score: float):
    if score >= 0.75:
        return "block"
    elif score >= 0.5:
        return "redact"
    else:
        return "allow"