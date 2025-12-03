# 🧭 Delhi Trip Planner (Structured Output LLM Project)

This project demonstrates how to use Google Gemini’s Structured Output feature to generate a clean, validated JSON trip plan for any city — currently implemented for Delhi.

# It includes:

- a Python script version

- a web interface (FastAPI) to generate JSON from browser

- mock mode (no API key needed)

- real Gemini mode (with API key)

Everything is validated using Pydantic JSON schema to ensure predictable, structured output.


## 🚀 Features

 ✔ Structured JSON Output using Gemini 2.5 Flash

 ✔ Pydantic Schema Validation

 ✔ Web Interface using FastAPI

 ✔ Mock Mode (works without API key)

 ✔ Real Mode (Gemini API key required)

 ✔ Day-wise places, descriptions, best time, weather

 ✔ Download/Copy JSON from browser

 ✔ Clean & simple UI

---

## 🏗 Tech Stack

- **Python 3**
- **FastAPI + Uvicorn (Web Interface)**
- **Google Gemini API (google-genai SDK)**
- **Pydantic v2 (JSON Schema)**
- **Mock JSON for offline/demo mode**
---
## ▶️ How to Run (Web App)

# 1. Install dependencies
```
pip install -r requirements.txt
```

# 2. Run in Mock Mode (No API key needed)
```
set USE_MOCK=true
python -m uvicorn web_app:app --reload
```

## Open:
```
 http://127.0.0.1:8000/
```

# 3. Run in Real Mode (Gemini API Key)
```
set GEMINI_API_KEY=YOUR_KEY
set USE_MOCK=false
python -m uvicorn web_app:app --reload
```

## 📌 Notes

- Never commit your API key to GitHub

- Use mock mode for safe demos

- Real mode requires a valid Gemini API key

---


