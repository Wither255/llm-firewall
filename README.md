# Setup & Usage

### Prerequisite
Install Ollama at Ollama.com

Install requirements
```bash
pip install -r requirements.txt
```

### 1. Setup local LLM for contextual risk scoring
Use Ollama with light model llama3.2 as the LLM Judge, then run:
```bash
ollama run llama3.2
```

### 2. Run firewall server
Run main to spin up firewall locally on 127.0.0.1:8000, can open API documentation page in a browser at http://127.0.0.1:8000/docs
```bash
python main.py
```

# For firewall WebUI;
```bash
python dashboard.py
```
The firewall has two tabs, one to test/try prompts and the other to display firewall message history.

# For prompt example testing firewall;
```bash
python testAPI.py
```
Script that passes pre-made prompts and compares them to expected action.
# For API test;
```bash
python mock_chatbot.py
```
Simple dummy program that sends queries and receives answers through firewall.
## API endpoints

API_URL = "http://127.0.0.1:8000/scan"

LOGS_URL = "http://127.0.0.1:8000/logs"


