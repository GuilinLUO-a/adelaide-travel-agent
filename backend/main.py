from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TravelPreferences(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)  # Strip leading/trailing whitespace from text.

    destination: str = Field(min_length=1)  # Require at least one character after whitespace is stripped.
    start_date: date  # Validate and convert incoming values to Python dates.
    end_date: date  # Validate and convert incoming values to Python dates.
    budget_aud: float = Field(gt=0, allow_inf_nan=False)  # Must be > 0; rejects infinity and NaN.
    travellers: int = Field(gt=0, strict=True)  # Requires an integer; rejects 1.5 and "1".
    interests: list[str] = Field(default_factory=list)  # Create an empty list when omitted.


    # mode="after" runs this check after the fields pass validation.
    # Returning self gives Pydantic the validated object.
    @model_validator(mode="after")
    def check_dates(self) -> "TravelPreferences":
        if self.end_date < self.start_date:
            raise ValueError(
                "End date must be on or after start date."
            )
        return self


app = FastAPI(title="Adelaide Travel Agent")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/trip-preferences", response_model=TravelPreferences)
def submit_preferences(preferences: TravelPreferences):
    return preferences