from fastapi.testclient import TestClient

from main import app


def test_endpoint_returns_places_and_routes():
    request_body = {
        "destination": "Adelaide",
        "start_date": "2026-11-01",
        "end_date": "2026-11-01",
        "budget_aud": 100,
        "travellers": 1,
        "interests": ["museums", "food"],
    }

    with TestClient(app) as client:
        response = client.post(
            "/api/itinerary/generate",
            json=request_body,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total_budget_aud"] == 100
    assert len(data["days"]) == 1

    day = data["days"][0]

    assert day["allocated_budget_aud"] == 100
    assert len(day["activities"]) == 3
    assert len(day["routes"]) == 2

    assert all(
        activity["place_status"] == "available"
        for activity in day["activities"]
    )

    assert [
        (route["from_period"], route["to_period"])
        for route in day["routes"]
    ] == [
        ("morning", "afternoon"),
        ("afternoon", "evening"),
    ]

    for index, route in enumerate(day["routes"]):
        assert route["status"] == "available"
        assert route["source"]["provider"] == "mock"
        assert route["distance_meters"] == 1400
        assert route["duration_seconds"] == 1080

        assert route["from_place_id"] == (
            day["activities"][index]["place"]["place_id"]
        )
        assert route["to_place_id"] == (
            day["activities"][index + 1]["place"]["place_id"]
        )