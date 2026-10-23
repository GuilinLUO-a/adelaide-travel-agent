import os
from collections.abc import Iterator

import httpx
from fastapi import HTTPException

from providers.base import PlaceProvider
from providers.google_places import GooglePlacesProvider
from providers.mock import MockPlaceProvider


def get_place_provider() -> Iterator[PlaceProvider]:
    provider_name = os.environ.get("PLACE_PROVIDER", "mock").strip().lower()

    if provider_name == "mock":
        yield MockPlaceProvider()
        return

    if provider_name != "google_places":
        raise HTTPException(
            status_code=503,
            detail="PLACE_PROVIDER must be mock or google_places.",
        )

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Google Places API key is not configured.",
        )

    with httpx.Client() as client:
        yield GooglePlacesProvider(api_key=api_key, client=client)