from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal
from itinerary import generate_itinerary


class TravelPreferences(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )  # Strip leading/trailing whitespace from text.

    destination: str = Field(
        min_length=1
    )  # Require at least one character after whitespace is stripped.
    start_date: date  # Validate and convert incoming values to Python dates.
    end_date: date  # Validate and convert incoming values to Python dates.
    budget_aud: float = Field(
        gt=0, allow_inf_nan=False
    )  # Must be > 0; rejects infinity and NaN.
    travellers: int = Field(
        gt=0, strict=True
    )  # Requires an integer; rejects 1.5 and "1".
    interests: list[str] = Field(
        default_factory=list
    )  # Create an empty list when omitted.

    # mode="after" runs this check after the fields pass validation.
    # Returning self gives Pydantic the validated object.
    @model_validator(mode="after")
    def check_dates(self) -> "TravelPreferences":
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date.")
        return self


class Activity(BaseModel):
    #  Restricts the period to only these three supported values.
    period: Literal["morning", "afternoon", "evening"]
    title: str


class ItineraryDay(BaseModel):
    day_number: int = Field(ge=1)
    date: date
    allocated_budget_aud: float = Field(ge=0)
    activities: list[Activity]


class ItineraryResponse(BaseModel):
    destination: str
    start_date: date
    end_date: date
    total_budget_aud: float
    travellers: int
    days: list[ItineraryDay]


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
