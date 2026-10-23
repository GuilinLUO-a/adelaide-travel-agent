from fastapi import Depends, FastAPI

from dependencies import get_place_provider
from itinerary_service import generate_enriched_itinerary
from models import ItineraryResponse, TravelPreferences
from providers.base import PlaceProvider


app = FastAPI(title="Adelaide Travel Agent")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/trip-preferences", response_model=TravelPreferences)
def submit_preferences(preferences: TravelPreferences):
    return preferences


@app.post("/api/itinerary/generate", response_model=ItineraryResponse)
def create_itinerary(
    preferences: TravelPreferences,
    provider: PlaceProvider = Depends(get_place_provider),
):
    return generate_enriched_itinerary(preferences, provider)