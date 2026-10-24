from datetime import datetime, timezone

import pytest

from models import Attribution, Place
from providers.mock import MockPlaceProvider


def test_museum_search_returns_place_candidates():
    provider = MockPlaceProvider()

    places = provider.search_places(
        destination="Adelaide",
        category="museums",
    )

    assert len(places) == 2
    assert all(isinstance(place, Place) for place in places)
    assert places[0].place_id == "mock-museum-1"


def test_food_search_returns_food_candidate():
    places = MockPlaceProvider().search_places(
        destination="Adelaide",
        category="food",
    )

    assert [place.place_id for place in places] == ["mock-market-1"]


def test_search_normalizes_case_and_whitespace():
    places = MockPlaceProvider().search_places(
        destination="  ADELAIDE  ",
        category="  MUSEUMS  ",
    )

    assert places[0].place_id == "mock-museum-1"


@pytest.mark.parametrize("category", ["unknown", ""])
def test_unknown_category_returns_empty_list(category):
    places = MockPlaceProvider().search_places(
        destination="Adelaide",
        category=category,
    )

    assert places == []


@pytest.mark.parametrize("destination", ["Sydney", ""])
def test_unsupported_destination_returns_empty_list(destination):
    places = MockPlaceProvider().search_places(
        destination=destination,
        category="museums",
    )

    assert places == []


def test_source_identifies_mock_and_current_utc_time():
    before = datetime.now(timezone.utc)

    places = MockPlaceProvider().search_places(
        destination="Adelaide",
        category="museums",
    )

    after = datetime.now(timezone.utc)

    for place in places:
        assert place.source.provider == "mock"
        assert place.source.retrieved_at.utcoffset().total_seconds() == 0
        assert before <= place.source.retrieved_at <= after


@pytest.mark.parametrize(
    "category",
    ["museums", "food", "nature", "beaches", "attractions"],
)
def test_all_supported_categories_return_valid_places(category):
    places = MockPlaceProvider().search_places(
        destination="Adelaide",
        category=category,
    )

    assert places

    for place in places:
        assert place.place_id.startswith("mock-")
        assert place.name.startswith("Mock")
        Place.model_validate(place.model_dump())


def test_results_are_independent_between_calls():
    provider = MockPlaceProvider()

    first = provider.search_places(destination="Adelaide", category="museums")
    first[0].name = "Changed"
    first[0].location.latitude = 0
    first[0].source.attributions.append(Attribution(label="Temporary"))
    first.clear()

    second = provider.search_places(destination="Adelaide", category="museums")

    assert len(second) == 2
    assert second[0].name == "Mock Museum"
    assert second[0].location.latitude == -34.920
    assert second[0].source.attributions == []


def test_candidate_order_is_repeatable():
    provider = MockPlaceProvider()

    first = provider.search_places(destination="Adelaide", category="museums")
    second = provider.search_places(destination="Adelaide", category="museums")

    assert [place.place_id for place in first] == [
        place.place_id for place in second
    ]