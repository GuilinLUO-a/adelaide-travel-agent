from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models import (
    Activity,
    Coordinates,
    DataSource,
    ItineraryResponse,
    Place,
    Route,
)


def make_source():
    return DataSource(
        provider="mock",
        retrieved_at=datetime.now(timezone.utc),
    )


def make_place():
    return Place(
        place_id="mock-museum-1",
        name="Example Museum",
        address="Example address, Adelaide",
        location={"latitude": -34.92, "longitude": 138.60},
        source=make_source(),
    )


def test_nested_place():
    place = make_place()

    assert place.location.latitude == -34.92
    assert place.model_dump(mode="json")["source"]["provider"] == "mock"


@pytest.mark.parametrize(
    "latitude, longitude",
    [
        (91, 138.60),
        (-34.92, 181),
        (float("nan"), 138.60),
        (-34.92, float("inf")),
    ],
)
def test_invalid_coordinates(latitude, longitude):
    with pytest.raises(ValidationError):
        Coordinates(latitude=latitude, longitude=longitude)


def test_blank_place_name():
    data = make_place().model_dump()
    data["name"] = "   "

    with pytest.raises(ValidationError):
        Place.model_validate(data)


def test_timestamp_requires_timezone():
    with pytest.raises(ValidationError):
        DataSource(
            provider="mock",
            retrieved_at="2026-10-22T10:00:00",
        )


def test_activity_requires_place_when_available():
    with pytest.raises(ValidationError):
        Activity(
            period="morning",
            title="Visit a museum",
            place_status="available",
        )


def test_activity_rejects_place_with_not_found():
    with pytest.raises(ValidationError):
        Activity(
            period="morning",
            title="Visit a museum",
            place_status="not_found",
            place=make_place(),
        )


def test_available_route_accepts_zero_values():
    route = Route(
        from_period="morning",
        to_period="afternoon",
        from_place_id="mock-a",
        to_place_id="mock-b",
        status="available",
        distance_meters=0,
        duration_seconds=0,
        source=make_source(),
    )

    assert route.duration_seconds == 0


def test_available_route_requires_travel_data():
    with pytest.raises(ValidationError):
        Route(
            from_period="morning",
            to_period="afternoon",
            from_place_id="mock-a",
            to_place_id="mock-b",
            status="available",
        )


def test_failed_route_cannot_include_distance():
    with pytest.raises(ValidationError):
        Route(
            from_period="morning",
            to_period="afternoon",
            from_place_id="mock-a",
            to_place_id="mock-b",
            status="provider_error",
            distance_meters=0,
        )


def test_existing_response_gains_defaults():
    response = ItineraryResponse.model_validate({
        "destination": "Adelaide",
        "start_date": "2026-11-10",
        "end_date": "2026-11-10",
        "total_budget_aud": 150,
        "travellers": 1,
        "days": [{
            "day_number": 1,
            "date": "2026-11-10",
            "allocated_budget_aud": 150,
            "activities": [{
                "period": "morning",
                "title": "Visit a museum",
            }],
        }],
    })

    data = response.model_dump(mode="json")

    assert data["warnings"] == []
    assert data["days"][0]["routes"] == []

    activity = data["days"][0]["activities"][0]

    assert activity["place_status"] == "not_requested"
    assert activity["place"] is None