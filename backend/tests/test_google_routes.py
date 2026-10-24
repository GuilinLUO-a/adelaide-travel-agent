import httpx
import pytest

from providers.google_routes import GoogleRoutesProvider, WALKING_NOTICE
from providers.mock import MockPlaceProvider
from providers.route_base import RouteProviderError


@pytest.fixture
def places():
    provider = MockPlaceProvider()

    origin = provider.search_places(
        destination="Adelaide", category="museums"
    )[0]

    destination = provider.search_places(
        destination="Adelaide", category="food"
    )[0]

    return origin, destination


def run_route_request(places, payload, status_code=200):
    def handler(request):
        return httpx.Response(status_code, json=payload)

    origin, destination = places

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GoogleRoutesProvider(
            api_key="test-key",
            client=client,
        )

        return provider.compute_route(
            origin=origin,
            destination=destination,
            from_period="morning",
            to_period="afternoon",
        )


def test_successful_route(places):
    route = run_route_request(places, {
        "routes": [{
            "distanceMeters": 1400,
            "duration": "1080s",
            "warnings": ["Sample route notice."],
        }]
    })

    origin, destination = places

    assert route.status == "available"
    assert route.from_place_id == origin.place_id
    assert route.to_place_id == destination.place_id
    assert route.distance_meters == 1400
    assert route.duration_seconds == 1080
    assert route.source.provider == "google_routes"
    assert WALKING_NOTICE in route.warnings
    assert "Sample route notice." in route.warnings


def test_no_route_found(places):
    route = run_route_request(places, {"routes": []})

    assert route.status == "not_found"
    assert route.distance_meters is None
    assert route.duration_seconds is None
    assert route.encoded_polyline is None
    assert route.source is None


def test_google_api_error(places):
    with pytest.raises(RouteProviderError) as caught:
        run_route_request(
            places,
            {"error": {"message": "Internal provider details"}},
            status_code=403,
        )

    assert "403" in str(caught.value)
    assert "Internal provider details" not in str(caught.value)