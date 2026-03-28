from fastapi import FastAPI
from pydantic import BaseModel
from scanner import scan_prompt
from policy import decide_action    # Separate for scalability
import time
from datetime import datetime

app = FastAPI(title="LLM Prompt Firewall")

# In-memory list to store firewall traffic for WebUI
scan_logs = []
MAX_LOGS = 50

class PromptRequest(BaseModel):
    prompt: str

class ScanResponse(BaseModel):
    prompt: str
    risk_score: float
    flags: list
    action: str
    timestamp: float

@app.get("/")
def root():
    return {"message": "LLM Firewall is running"}

# Endpoint to retrieve logs 
@app.get("/logs")
def get_logs():
    return {"logs": scan_logs}

@app.post("/scan", response_model=ScanResponse)
def scan(req: PromptRequest):
    result = scan_prompt(req.prompt)
    action = decide_action(result["score"])

    # Save the request details to our log list 
    log_entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": action.upper(),
        "score": round(result["score"], 2),
        "prompt": req.prompt,
        "flags": ", ".join(result["flags"]) if result["flags"] else "None"
    }
    
    # Newest entry first
    scan_logs.insert(0, log_entry)
    
    # Flush memory
    if len(scan_logs) > MAX_LOGS:
        scan_logs.pop()

    return ScanResponse(
        prompt=req.prompt,
        risk_score=result["score"],
        flags=result["flags"],
        action=action,
        timestamp=time.time()
    )