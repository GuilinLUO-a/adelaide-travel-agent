from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal
from itinerary import generate_itinerary
from models import ItineraryResponse, TravelPreferences

app = FastAPI(title="Adelaide Travel Agent")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/trip-preferences", response_model=TravelPreferences)
def submit_preferences(preferences: TravelPreferences):
    return preferences


@app.post("/api/itinerary/generate",response_model=ItineraryResponse)
def create_itinerary(preferences: TravelPreferences):

    itinerary = generate_itinerary(
        destination=preferences.destination,
        start_date=preferences.start_date,
        end_date=preferences.end_date,
        budget_aud=preferences.budget_aud,
        travellers=preferences.travellers,
        interests=preferences.interests,
    )

    return itinerary
