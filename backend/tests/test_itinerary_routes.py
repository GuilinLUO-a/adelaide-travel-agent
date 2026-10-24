from models import ItineraryResponse, Route, TravelPreferences
from itinerary_service import generate_enriched_itinerary
from providers.mock import MockPlaceProvider
from providers.mock_routes import MockRouteProvider
from route_service import enrich_itinerary_routes
from unittest.mock import Mock

from providers.route_base import RouteProvider, RouteProviderError


def test_adds_two_routes_to_one_day():
    preferences = TravelPreferences(
        destination="Adelaide",
        start_date="2026-11-01",
        end_date="2026-11-01",
        budget_aud=100,
        travellers=1,
        interests=["museums", "food"],
    )

    original = generate_enriched_itinerary(
        preferences,
        MockPlaceProvider(),
    )

    result = enrich_itinerary_routes(
        original,
        MockRouteProvider(),
    )

    day = result.days[0]

    assert len(day.routes) == 2

    assert [
        (route.from_period, route.to_period)
        for route in day.routes
    ] == [
        ("morning", "afternoon"),
        ("afternoon", "evening"),
    ]

    for index, route in enumerate(day.routes):
        assert route.status == "available"
        assert route.from_place_id == day.activities[index].place.place_id
        assert route.to_place_id == day.activities[index + 1].place.place_id
        assert route.source.provider == "mock"

    assert day.activities == original.days[0].activities
    assert day.allocated_budget_aud == original.days[0].allocated_budget_aud
    assert original.days[0].routes == []
    
def make_placed_itinerary():
    preferences = TravelPreferences(
        destination="Adelaide",
        start_date="2026-11-01",
        end_date="2026-11-01",
        budget_aud=100,
        travellers=1,
        interests=["museums", "food"],
    )

    return generate_enriched_itinerary(
        preferences,
        MockPlaceProvider(),
    )
    
def test_missing_afternoon_place_skips_both_routes():
    original = make_placed_itinerary()
    data = original.model_dump()

    afternoon = data["days"][0]["activities"][1]
    afternoon["place_status"] = "not_found"
    afternoon["place"] = None

    itinerary = ItineraryResponse.model_validate(data)

    provider = Mock(spec=RouteProvider)
    result = enrich_itinerary_routes(itinerary, provider)

    provider.compute_route.assert_not_called()

    assert result.days[0].routes == []
    assert result.days[0].activities == itinerary.days[0].activities

    assert any(
        "morning to afternoon: walking route skipped" in warning
        for warning in result.warnings
    )
    assert any(
        "afternoon to evening: walking route skipped" in warning
        for warning in result.warnings
    )
    
def test_no_walking_routes_found():
    itinerary = make_placed_itinerary()
    provider = Mock(spec=RouteProvider)

    def no_route(*, origin, destination, from_period, to_period):
        return Route(
            from_period=from_period,
            to_period=to_period,
            from_place_id=origin.place_id,
            to_place_id=destination.place_id,
            status="not_found",
        )

    provider.compute_route.side_effect = no_route

    result = enrich_itinerary_routes(itinerary, provider)

    assert provider.compute_route.call_count == 2
    assert len(result.days[0].routes) == 2

    for route in result.days[0].routes:
        assert route.status == "not_found"
        assert route.distance_meters is None
        assert route.duration_seconds is None
        assert route.encoded_polyline is None
        assert route.source is None

    assert result.days[0].activities == itinerary.days[0].activities

    assert any(
        "no walking route was found" in warning
        for warning in result.warnings
    )
    
def test_first_route_failure_preserves_second_route():
    itinerary = make_placed_itinerary()
    activities = itinerary.days[0].activities

    second_route = MockRouteProvider().compute_route(
        origin=activities[1].place,
        destination=activities[2].place,
        from_period="afternoon",
        to_period="evening",
    )

    provider = Mock(spec=RouteProvider)
    provider.compute_route.side_effect = [
        RouteProviderError("Internal provider details"),
        second_route,
    ]

    result = enrich_itinerary_routes(itinerary, provider)
    first, second = result.days[0].routes

    assert provider.compute_route.call_count == 2

    assert first.status == "provider_error"
    assert first.distance_meters is None
    assert first.duration_seconds is None
    assert first.encoded_polyline is None
    assert first.source is None

    assert second == second_route
    assert result.days[0].activities == itinerary.days[0].activities
    assert result.total_budget_aud == itinerary.total_budget_aud

    assert any(
        "temporarily unavailable" in warning
        for warning in result.warnings
    )
    assert all(
        "Internal provider details" not in warning
        for warning in result.warnings
    )