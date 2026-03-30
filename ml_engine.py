# ml_engine.py

from transformers import pipeline

print("Loading ML Pipeline...")

try:
    # Initialize pipeline globally so it only loads into memory once
    classifier = pipeline(
        "text-classification",
        model="ProtectAI/deberta-v3-base-prompt-injection-v2",
        device=-1 # Set to 0 if you have a dedicated GPU configured with PyTorch
    )
except Exception as e:
    print(f"ML model failed to load. {e}")
    classifier = None

def get_ml_risk_score(prompt: str) -> float:
    # Passes the prompt to the Hugging Face model and returns a normalized risk score.
    if not classifier:
        return 0.0
    
    # Truncate prompt to avoid exceeding token limits (usually 512 for BERT models)
    truncated_prompt = prompt[:1500] 
    
    results = classifier(truncated_prompt)
    result = results[0]
    
    # The model outputs labels like 'INJECTION' or 'SAFE'. We convert this to a 0-1 scale.
    if result['label'] == 'INJECTION':
        return result['score']
    else:
        # If safe, risk score is inverse of confidence
        return 1.0 - result['score']