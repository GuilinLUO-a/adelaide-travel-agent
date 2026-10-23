import json

import httpx
import pytest
from fastapi.testclient import TestClient

from dependencies import get_place_provider
from itinerary import generate_itinerary, get_activity_categories
from itinerary_service import generate_enriched_itinerary
from main import app
from models import TravelPreferences
from providers.base import PlaceProviderError
from providers.google_places import GooglePlacesProvider
from providers.mock import MockPlaceProvider


def make_preferences(**changes):
    data = {
        "destination": "Adelaide",
        "start_date": "2026-11-10",
        "end_date": "2026-11-10",
        "budget_aud": 150,
        "travellers": 1,
        "interests": ["museums", "food"],
    }
    data.update(changes)
    return TravelPreferences.model_validate(data)


class RecordingProvider:
    def __init__(self, *, fail_category=None, empty=False):
        self.calls = []
        self.fail_category = fail_category
        self.empty = empty
        self.mock = MockPlaceProvider()

    def search_places(self, *, destination, category):
        self.calls.append(category)
        if category == self.fail_category:
            raise PlaceProviderError("Sensitive internal provider details")
        if self.empty:
            return []
        return self.mock.search_places(destination=destination, category=category)


@pytest.fixture
def client_for_provider():
    def make_client(provider):
        def override():
            return provider
        app.dependency_overrides[get_place_provider] = override
        return TestClient(app)

    try:
        yield make_client
    finally:
        app.dependency_overrides.pop(get_place_provider, None)


@pytest.mark.parametrize("interests, day_number, expected", [
    (["museums", "food"], 1, ["museums", "food", "museums"]),
    (["museums", "food"], 2, ["food", "museums", "food"]),
    ([], 1, ["attractions", "attractions", "attractions"]),
])
def test_category_assignment(interests, day_number, expected):
    assert get_activity_categories(interests, day_number) == expected


def test_places_preserve_base_itinerary():
    preferences = make_preferences()
    base = generate_itinerary(**preferences.model_dump())
    result = generate_enriched_itinerary(preferences, RecordingProvider())
    day = result.days[0]

    assert result.start_date == base["start_date"]
    assert result.end_date == base["end_date"]
    assert result.total_budget_aud == base["total_budget_aud"]
    assert day.allocated_budget_aud == base["days"][0]["allocated_budget_aud"]
    assert [activity.title for activity in day.activities] == [
        activity["title"] for activity in base["days"][0]["activities"]
    ]
    assert all(activity.place_status == "available" for activity in day.activities)
    assert len({activity.place.place_id for activity in day.activities}) == 3
    assert any("mock" in warning for warning in result.warnings)
    assert day.routes == []


def test_empty_results_preserve_activities():
    result = generate_enriched_itinerary(
        make_preferences(), RecordingProvider(empty=True)
    )
    assert len(result.days[0].activities) == 3
    assert all(
        activity.place_status == "not_found" and activity.place is None
        for activity in result.days[0].activities
    )
    assert result.warnings


def test_no_duplicate_place_when_candidates_run_out():
    result = generate_enriched_itinerary(
        make_preferences(interests=["museums"]), RecordingProvider()
    )
    activities = result.days[0].activities
    assert activities[0].place.place_id != activities[1].place.place_id
    assert activities[2].place_status == "not_found"
    assert activities[2].place is None
    assert any("No unused" in warning for warning in result.warnings)


def test_lookups_are_once_per_category_per_request():
    provider = RecordingProvider()
    preferences = make_preferences(end_date="2026-11-12")

    first = generate_enriched_itinerary(preferences, provider)
    assert provider.calls == ["museums", "food"]
    assert len(first.days) == 3
    assert sum(round(day.allocated_budget_aud * 100) for day in first.days) == 15000

    generate_enriched_itinerary(preferences, provider)
    assert provider.calls == ["museums", "food", "museums", "food"]


def test_unsupported_destination_skips_lookup():
    provider = RecordingProvider()
    result = generate_enriched_itinerary(
        make_preferences(destination="Sydney"), provider
    )
    assert provider.calls == []
    assert all(
        activity.place_status == "not_requested"
        for activity in result.days[0].activities
    )
    assert any("Adelaide only" in warning for warning in result.warnings)


def test_api_preserves_partial_results_after_failure(client_for_provider):
    with client_for_provider(RecordingProvider(fail_category="food")) as client:
        response = client.post(
            "/api/itinerary/generate",
            json=make_preferences().model_dump(mode="json"),
        )

    assert response.status_code == 200
    data = response.json()
    activities = data["days"][0]["activities"]
    assert [activity["place_status"] for activity in activities] == [
        "available", "provider_error", "available"
    ]
    assert activities[1]["place"] is None
    assert activities[1]["title"] == "Explore a food market"
    assert data["warnings"]
    assert "Sensitive" not in " ".join(data["warnings"])


def test_api_google_adapter_integration(client_for_provider):
    calls = []

    def handler(request):
        query = json.loads(request.content)["textQuery"]
        calls.append(query)
        ids = ["test-food"] if "restaurants" in query else [
            "test-museum-1", "test-museum-2"
        ]
        return httpx.Response(200, json={
            "places": [{
                "id": place_id,
                "displayName": {"text": f"Example {place_id}"},
                "formattedAddress": "Example address, Adelaide",
                "location": {"latitude": -34.92, "longitude": 138.60},
            } for place_id in ids],
        })

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        provider = GooglePlacesProvider(api_key="test-key", client=http_client)
        with client_for_provider(provider) as client:
            response = client.post(
                "/api/itinerary/generate",
                json=make_preferences().model_dump(mode="json"),
            )

    assert response.status_code == 200
    activities = response.json()["days"][0]["activities"]
    assert all(activity["place_status"] == "available" for activity in activities)
    assert all(
        activity["place"]["source"]["provider"] == "google_places"
        for activity in activities
    )
    assert len(calls) == 2


@pytest.mark.parametrize("field, value", [
    ("budget_aud", 0),
    ("travellers", 1.5),
])
def test_api_still_validates_preferences(client_for_provider, field, value):
    provider = RecordingProvider()
    payload = make_preferences().model_dump(mode="json")
    payload[field] = value

    with client_for_provider(provider) as client:
        response = client.post("/api/itinerary/generate", json=payload)

    assert response.status_code == 422
    assert provider.calls == []


def test_api_mock_configuration(monkeypatch):
    monkeypatch.setenv("PLACE_PROVIDER", "mock")
    with TestClient(app) as client:
        response = client.post(
            "/api/itinerary/generate",
            json=make_preferences().model_dump(mode="json"),
        )
    assert response.status_code == 200
    place = response.json()["days"][0]["activities"][0]["place"]
    assert place["source"]["provider"] == "mock"


@pytest.mark.parametrize("provider_name", ["unknown", "google_places"])
def test_api_rejects_invalid_configuration(monkeypatch, provider_name):
    monkeypatch.setenv("PLACE_PROVIDER", provider_name)
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "")
    with TestClient(app) as client:
        response = client.post(
            "/api/itinerary/generate",
            json=make_preferences().model_dump(mode="json"),
        )
    assert response.status_code == 503