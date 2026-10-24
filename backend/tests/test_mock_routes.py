from datetime import datetime, timezone

from providers.mock import MockPlaceProvider
from providers.mock_routes import MockRouteProvider


def get_test_places():
    provider = MockPlaceProvider()

    museum = provider.search_places(
        destination="Adelaide",
        category="museums",
    )[0]

    market = provider.search_places(
        destination="Adelaide",
        category="food",
    )[0]

    return museum, market


def test_mock_route_connects_requested_places():
    museum, market = get_test_places()
    provider = MockRouteProvider()

    before = datetime.now(timezone.utc)

    route = provider.compute_route(
        origin=museum,
        destination=market,
        from_period="morning",
        to_period="afternoon",
    )

    after = datetime.now(timezone.utc)

    assert route.from_place_id == museum.place_id
    assert route.to_place_id == market.place_id
    assert route.from_period == "morning"
    assert route.to_period == "afternoon"
    assert route.travel_mode == "walking"
    assert route.status == "available"
    assert route.distance_meters == 1400
    assert route.duration_seconds == 1080
    assert route.is_estimate is True
    assert route.encoded_polyline is None
    assert route.source.provider == "mock"
    assert before <= route.source.retrieved_at <= after


def test_return_journey_uses_reversed_place_ids():
    museum, market = get_test_places()
    provider = MockRouteProvider()

    route = provider.compute_route(
        origin=market,
        destination=museum,
        from_period="afternoon",
        to_period="evening",
    )

    assert route.from_place_id == market.place_id
    assert route.to_place_id == museum.place_id
    assert route.from_period == "afternoon"
    assert route.to_period == "evening"