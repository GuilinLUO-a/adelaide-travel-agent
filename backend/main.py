from fastapi import Depends, FastAPI

from dependencies import get_place_provider, get_route_provider
from itinerary_service import generate_enriched_itinerary
from models import ItineraryResponse, TravelPreferences
from providers.base import PlaceProvider
from providers.route_base import RouteProvider
from route_service import enrich_itinerary_routes


app = FastAPI(title="Adelaide Travel Agent")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/trip-preferences", response_model=TravelPreferences)
def submit_preferences(preferences: TravelPreferences):
    return preferences


@app.post(
    "/api/itinerary/generate",
    response_model=ItineraryResponse,
)
def generate_itinerary_endpoint(
    preferences: TravelPreferences,
    place_provider: PlaceProvider = Depends(get_place_provider),
    route_provider: RouteProvider = Depends(get_route_provider),
) -> ItineraryResponse:
    itinerary = generate_enriched_itinerary(
        preferences,
        place_provider,
    )

    return enrich_itinerary_routes(
        itinerary,
        route_provider,
    )