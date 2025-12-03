# web_app.py -- Fixed template escaping + Gemini mock mode + error handling
import os
import json
import traceback
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from typing import List

# Use mock by default; set USE_MOCK=false to try real Gemini (requires GEMINI_API_KEY)
USE_MOCK = os.environ.get("USE_MOCK", "true").lower() in ("1", "true", "yes")

if not USE_MOCK:
    from google import genai

# ========== Pydantic schema ==========
class Place(BaseModel):
    name: str = Field(description="Place name")
    description: str = Field(description="Short description")
    best_time: str = Field(description="Best time to visit")

class Weather(BaseModel):
    temperature: str = Field(description="Temperature summary")
    condition: str = Field(description="Weather condition like sunny/hazy")
    advice: str = Field(description="Clothing or health advice")

class TripPlan(BaseModel):
    city: str
    days: int
    places_to_visit: List[Place]
    weather: Weather

app = FastAPI()

SAMPLE_JSON = {
    "city": "New Delhi",
    "days": 3,
    "places_to_visit": [
        {"name": "India Gate", "description": "A war memorial ...", "best_time": "Morning or late afternoon"},
        {"name": "Humayun's Tomb", "description": "Magnificent Mughal tomb ...", "best_time": "Morning (9-12)"},
        {"name": "Qutub Minar", "description": "UNESCO site ...", "best_time": "Late morning"}
    ],
    "weather": {"temperature": "20°C to 30°C", "condition": "Sunny", "advice": "Light clothes, sunscreen"}
}

# Note: all literal { and } in the template are doubled to escape .format()
HTML_PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Trip Planner — JSON Generator</title>
    <style>
      body{{font-family:Arial,Helvetica,sans-serif;background:#f5f7fb;margin:0}}
      .card{{max-width:900px;margin:36px auto;background:#fff;padding:24px;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,0.08)}}
      h1{{margin-top:0}}
      label{{font-weight:600}}
      input,textarea,select{{width:100%;padding:10px;margin:8px 0 14px;border-radius:6px;border:1px solid #dcdde1}}
      button{{background:#0b78ff;color:#fff;padding:10px 14px;border:none;border-radius:8px;cursor:pointer}}
      pre{{background:#111827;color:#e6eef8;padding:16px;border-radius:8px;overflow:auto;white-space:pre-wrap}}
      .controls{{display:flex;gap:10px}}
      .small{{width:150px}}
      .actions{{margin-top:10px;display:flex;gap:8px}}
      a.download{{display:inline-block;padding:8px 12px;background:#06b6d4;color:#fff;border-radius:6px;text-decoration:none}}
      .error{{background:#ffe3e3;color:#7a1506;padding:10px;border-radius:6px}}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Trip Planner — JSON Generator</h1>
      <form method="post" action="/generate">
        <label>City</label>
        <input name="city" value="{city}" />

        <label>Days</label>
        <input name="days" type="number" value="{days}" min="1" />

        <label>Preferences (space-separated)</label>
        <input name="preferences" value="{prefs}" placeholder="heritage food nightlife" />

        <label>Mode</label>
        <select name="mode">
          <option value="real" {real_selected}>Real (Gemini)</option>
          <option value="mock" {mock_selected}>Mock (no API key)</option>
        </select>

        <div class="actions">
          <button type="submit">Generate JSON</button>
        </div>
      </form>

      <hr/>
      <div id="output">
        {result_html}
      </div>
    </div>
  </body>
</html>
"""

def render_page(result_html: str = "<i>JSON result will appear here.</i>",
                city: str = "New Delhi", days: int = 3, prefs: str = "", mode: str = "mock"):
    return HTML_PAGE.format(
        result_html=result_html,
        city=city,
        days=days,
        prefs=prefs,
        real_selected="selected" if mode == "real" else "",
        mock_selected="selected" if mode == "mock" else ""
    )

@app.get("/", response_class=HTMLResponse)
async def home():
    return render_page()

@app.post("/generate", response_class=HTMLResponse)
async def generate(city: str = Form(...), days: int = Form(...), preferences: str = Form(""),
                   mode: str = Form("mock")):
    try:
        # choose mock or real
        if mode == "mock" or USE_MOCK:
            output = SAMPLE_JSON.copy()
            output["city"] = city
            output["days"] = int(days)
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY not set. Set it or use mock mode.")

            client = genai.Client(api_key=api_key)

            prompt = f"""Plan a {days}-day trip to {city}. Preferences: {preferences}.
Return ONLY valid JSON matching the following schema: {TripPlan.model_json_schema()}.
Provide places with name, description and best_time, and weather (temperature, condition, advice)."""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": TripPlan.model_json_schema(),
                },
            )

            output = TripPlan.model_validate_json(response.text).model_dump()

        pretty = json.dumps(output, indent=2, ensure_ascii=False)

        result_html = f"""
          <div>
            <div style="margin-bottom:8px;">
              <a class="download" href="/download?city={city}&days={days}&prefs={preferences}&mode={mode}">Download JSON</a>
              <button onclick="navigator.clipboard.writeText(document.getElementById('jsonblob').innerText)">Copy JSON</button>
            </div>
            <pre id="jsonblob">{pretty}</pre>
          </div>
        """
        return render_page(result_html=result_html, city=city, days=days, prefs=preferences, mode=mode)

    except Exception as exc:
        tb = traceback.format_exc()
        err_html = f"<div class='error'><b>Error:</b> {str(exc)}<pre style='white-space:pre-wrap;margin-top:8px'>{tb}</pre></div>"
        return render_page(result_html=err_html, city=city, days=days, prefs=preferences, mode=mode)

@app.get("/download")
async def download(city: str = "New Delhi", days: int = 3, prefs: str = "", mode: str = "mock"):
    output = SAMPLE_JSON.copy()
    output["city"] = city
    output["days"] = int(days)
    content = json.dumps(output, indent=2, ensure_ascii=False)
    headers = {
        "Content-Disposition": f'attachment; filename="trip_{city}_{days}days.json"'
    }
    return Response(content=content, media_type="application/json", headers=headers)
