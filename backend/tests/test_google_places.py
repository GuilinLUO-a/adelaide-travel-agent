import json
from datetime import datetime, timezone

import httpx
import pytest

from providers.base import PlaceProviderError
from providers.google_places import GooglePlacesProvider


def example_place():
    return {
        "id": "test-place-1",
        "displayName": {"text": "Example Museum"},
        "formattedAddress": "Example address, Adelaide",
        "location": {"latitude": -34.92, "longitude": 138.60},
    }


def search_with_payload(payload):
    def handler(request):
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)
        return provider.search_places(destination="Adelaide", category="museums")


def test_request_and_conversion():
    def handler(request):
        assert request.method == "POST"
        assert str(request.url) == (
            "https://places.googleapis.com/v1/places:searchText"
        )
        assert request.headers["X-Goog-Api-Key"] == "test-key"
        assert set(request.headers["X-Goog-FieldMask"].split(",")) == {
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.attributions",
        }

        body = json.loads(request.content)

        assert body["textQuery"] == (
            "museums in Adelaide, South Australia, Australia"
        )
        assert body["pageSize"] == 5
        assert body["languageCode"] == "en"

        return httpx.Response(200, json={"places": [example_place()]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)
        places = provider.search_places(
            destination="  ADELAIDE  ",
            category="  MUSEUMS  ",
        )

    assert places[0].place_id == "test-place-1"
    assert places[0].name == "Example Museum"
    assert places[0].address == "Example address, Adelaide"
    assert places[0].location.latitude == -34.92
    assert places[0].source.provider == "google_places"


def test_attributions_are_preserved():
    record = example_place()
    record["attributions"] = [
        {"provider": "Example data provider", "providerUri": "https://example.com"},
        {"provider": "Another provider"},
    ]

    places = search_with_payload({"places": [record]})
    credits = places[0].source.attributions

    assert credits[0].label == "Example data provider"
    assert str(credits[0].url) == "https://example.com/"
    assert credits[1].url is None


@pytest.mark.parametrize("payload", [{}, {"places": []}])
def test_empty_results(payload):
    assert search_with_payload(payload) == []


@pytest.mark.parametrize("payload", [
    [],
    None,
    {"places": None},
    {"places": {}},
    {"places": [{}]},
    {"error": {"message": "sensitive provider details"}},
])
def test_invalid_payload(payload):
    with pytest.raises(PlaceProviderError):
        search_with_payload(payload)


@pytest.mark.parametrize("field, value", [
    ("id", ""),
    ("formattedAddress", "   "),
    ("displayName", {"text": ""}),
    ("location", {"latitude": 95, "longitude": 138.60}),
    ("attributions", [{"provider": ""}]),
])
def test_invalid_place_fields(field, value):
    record = example_place()
    record[field] = value

    with pytest.raises(PlaceProviderError):
        search_with_payload({"places": [record]})


@pytest.mark.parametrize("status", [403, 429, 500])
def test_http_errors_use_safe_messages(status):
    def handler(request):
        return httpx.Response(
            status,
            json={"error": {"message": "sensitive provider details"}},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)

        with pytest.raises(PlaceProviderError) as caught:
            provider.search_places(destination="Adelaide", category="museums")

    assert f"HTTP {status}" in str(caught.value)
    assert "sensitive provider details" not in str(caught.value)


@pytest.mark.parametrize("error_type", [httpx.ReadTimeout, httpx.ConnectError])
def test_network_errors(error_type):
    def handler(request):
        raise error_type("sensitive network details", request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)

        with pytest.raises(PlaceProviderError) as caught:
            provider.search_places(destination="Adelaide", category="museums")

    assert str(caught.value) == "Google Places could not be reached."


def test_invalid_json():
    def handler(request):
        return httpx.Response(200, content=b"not JSON")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)

        with pytest.raises(PlaceProviderError, match="invalid JSON"):
            provider.search_places(destination="Adelaide", category="museums")


@pytest.mark.parametrize("destination, category", [
    ("Sydney", "museums"),
    ("Adelaide", "unknown"),
])
def test_unsupported_search_makes_no_request(destination, category):
    def handler(request):
        pytest.fail("An unsupported search should not make an HTTP request.")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GooglePlacesProvider(api_key="test-key", client=client)

        assert provider.search_places(
            destination=destination,
            category=category,
        ) == []


@pytest.mark.parametrize("api_key", ["", "   "])
def test_missing_api_key(api_key):
    with httpx.Client(transport=httpx.MockTransport(lambda request: None)) as client:
        with pytest.raises(PlaceProviderError, match="not configured"):
            GooglePlacesProvider(api_key=api_key, client=client)


def test_retrieval_time_is_current_utc():
    before = datetime.now(timezone.utc)
    places = search_with_payload({"places": [example_place()]})
    after = datetime.now(timezone.utc)

    timestamp = places[0].source.retrieved_at

    assert before <= timestamp <= after
    assert timestamp.utcoffset().total_seconds() == 0