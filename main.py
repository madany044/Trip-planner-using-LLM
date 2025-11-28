from google import genai
from pydantic import BaseModel, Field
from typing import List

# ---- Create Client with API key ----
client = genai.Client(api_key="AIzaSyB_NntdzhHH41f6I9nC9aYsnnhuJdn5dtI")

# ---------- Schema ----------
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

prompt = """
Plan a 3-day holiday trip to Delhi. Give places, timings, descriptions, and weather advice.
Return ONLY JSON following the schema.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": TripPlan.model_json_schema(),
    },
)

# Validate JSON returned by the model
trip = TripPlan.model_validate_json(response.text)

# Print nicely using pydantic v2 method
print(trip.model_dump_json(indent=2))

# Save to file
with open("sample_output.json", "w", encoding="utf-8") as f:
    f.write(trip.model_dump_json(indent=2))
