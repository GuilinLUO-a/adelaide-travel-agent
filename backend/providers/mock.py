from datetime import datetime, timezone

from models import DataSource, Place


# Synthetic fixtures only: these are not verified travel recommendations.
_MOCK_PLACES = {
    "museums": [
        {
            "place_id": "mock-museum-1",
            "name": "Mock Museum",
            "address": "Mock address A, Adelaide",
            "location": {"latitude": -34.920, "longitude": 138.600},
        },
        {
            "place_id": "mock-gallery-1",
            "name": "Mock Gallery",
            "address": "Mock address B, Adelaide",
            "location": {"latitude": -34.925, "longitude": 138.605},
        },
    ],
    "food": [
        {
            "place_id": "mock-market-1",
            "name": "Mock Market",
            "address": "Mock address C, Adelaide",
            "location": {"latitude": -34.930, "longitude": 138.600},
        },
    ],
    "nature": [
        {
            "place_id": "mock-garden-1",
            "name": "Mock Garden",
            "address": "Mock address D, Adelaide",
            "location": {"latitude": -34.915, "longitude": 138.610},
        },
    ],
    "beaches": [
        {
            "place_id": "mock-beach-1",
            "name": "Mock Beach",
            "address": "Mock address E, Adelaide",
            "location": {"latitude": -34.980, "longitude": 138.510},
        },
    ],
    "attractions": [
        {
            "place_id": "mock-attraction-1",
            "name": "Mock City Attraction",
            "address": "Mock address F, Adelaide",
            "location": {"latitude": -34.927, "longitude": 138.599},
        },
    ],
}

class MockPlaceProvider:
    def search_places(
        self,
        *,
        destination: str,
        category: str,
    ) -> list[Place]:
        if destination.strip().lower() != "adelaide":
            return []

        records = _MOCK_PLACES.get(category.strip().lower(), [])
        retrieved_at = datetime.now(timezone.utc)
        places = []

        for record in records:
            place = Place(
                **record,
                source=DataSource(
                    provider="mock",
                    retrieved_at=retrieved_at,
                ),
            )
            places.append(place)

        return places