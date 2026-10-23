from datetime import date
from typing import Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


ActivityPeriod = Literal["morning", "afternoon", "evening"]


class AppModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class TravelPreferences(AppModel):
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date
    budget_aud: float = Field(gt=0, allow_inf_nan=False)
    travellers: int = Field(gt=0, strict=True)
    interests: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_dates(self) -> "TravelPreferences":
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date.")
        return self
    
class Coordinates(AppModel):
    latitude: float = Field(
        ge=-90, le=90, allow_inf_nan=False, strict=True # The adapter should supply numeric values.
    )
    longitude: float = Field(
        ge=-180, le=180, allow_inf_nan=False, strict=True
    )


class Attribution(AppModel):
    label: str = Field(min_length=1)
    url: HttpUrl | None = None


class DataSource(AppModel):
    provider: Literal["mock", "google_places", "google_routes"]
    retrieved_at: AwareDatetime # Accepts a timestamp and Rejects a timestamp without a timezone
    attributions: list[Attribution] = Field(default_factory=list)
    
class Place(AppModel):
    place_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    location: Coordinates
    source: DataSource

    @model_validator(mode="after")
    def check_source(self) -> "Place":
        if self.source.provider not in ("mock", "google_places"):
            raise ValueError("A place requires a mock or Google Places source.")
        return self
    
class Route(AppModel):
    from_period: ActivityPeriod
    to_period: ActivityPeriod
    from_place_id: str = Field(min_length=1)
    to_place_id: str = Field(min_length=1)
    travel_mode: Literal["walking"] = "walking"
    status: Literal["available", "not_found", "provider_error"]

    distance_meters: float | None = Field(
        default=None, ge=0, allow_inf_nan=False, strict=True
    )
    duration_seconds: float | None = Field(
        default=None, ge=0, allow_inf_nan=False, strict=True
    )
    is_estimate: Literal[True] = True
    encoded_polyline: str | None = Field(default=None, min_length=1)
    source: DataSource | None = None

    @model_validator(mode="after")
    def check_route(self) -> "Route":
        if (self.from_period, self.to_period) not in (
            ("morning", "afternoon"),
            ("afternoon", "evening"),
        ):
            raise ValueError("Routes must connect consecutive activity periods.")

        if self.status == "available":
            if (
                self.distance_meters is None
                or self.duration_seconds is None
                or self.source is None
            ):
                raise ValueError(
                    "An available route requires distance, duration, and source."
                )

            if self.source.provider not in ("mock", "google_routes"):
                raise ValueError(
                    "A route requires a mock or Google Routes source."
                )
        elif (
            self.distance_meters is not None
            or self.duration_seconds is not None
            or self.encoded_polyline is not None
            or self.source is not None
        ):
            raise ValueError(
                "An unavailable route must have null travel data and source."
            )

        return self
    
class Activity(AppModel):
    period: ActivityPeriod
    title: str
    place_status: Literal[
        "not_requested", "available", "not_found", "provider_error"
    ] = "not_requested"
    place: Place | None = None

    @model_validator(mode="after")
    def check_place(self) -> "Activity":
        if self.place_status == "available":
            if self.place is None:
                raise ValueError("An available activity requires a place.")
        elif self.place is not None:
            raise ValueError(
                "A place is only allowed when place_status is available."
            )

        return self


class ItineraryDay(AppModel):
    day_number: int = Field(ge=1)
    date: date
    allocated_budget_aud: float = Field(ge=0)
    activities: list[Activity]
    routes: list[Route] = Field(default_factory=list)


class ItineraryResponse(AppModel):
    destination: str
    start_date: date
    end_date: date
    total_budget_aud: float
    travellers: int
    days: list[ItineraryDay]
    warnings: list[str] = Field(default_factory=list)