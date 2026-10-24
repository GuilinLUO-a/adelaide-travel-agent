from datetime import datetime, timezone

import httpx
from pydantic import Field, HttpUrl, ValidationError

from models import AppModel, Attribution, Coordinates, DataSource, Place
from providers.base import PlaceProviderError


SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.attributions",
])

_SEARCH_TERMS = {
    "museums": "museums",
    "food": "restaurants and food markets",
    "nature": "parks and gardens",
    "beaches": "beaches",
    "attractions": "tourist attractions",
}


class _GoogleText(AppModel):
    text: str = Field(min_length=1)


class _GoogleAttribution(AppModel):
    provider: str = Field(min_length=1)
    providerUri: HttpUrl | None = None


class _GooglePlace(AppModel):
    id: str = Field(min_length=1)
    displayName: _GoogleText
    formattedAddress: str = Field(min_length=1)
    location: Coordinates
    attributions: list[_GoogleAttribution] = Field(default_factory=list)


class GooglePlacesProvider:
    def __init__(self, *, api_key: str, client: httpx.Client):
        if not api_key.strip():
            raise PlaceProviderError("Google Places API key is not configured.")

        self._api_key = api_key.strip()
        self._client = client

    def search_places(
        self,
        *,
        destination: str,
        category: str,
    ) -> list[Place]:
        if destination.strip().lower() != "adelaide":
            return []

        search_terms = _SEARCH_TERMS.get(category.strip().lower())
        if search_terms is None:
            return []

        try:
            response = self._client.post(
                SEARCH_URL,
                headers={
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": FIELD_MASK,
                },
                json={
                    "textQuery": (
                        f"{search_terms} in Adelaide, South Australia, Australia"
                    ),
                    "languageCode": "en",
                    "regionCode": "AU",
                    "pageSize": 5,
                },
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise PlaceProviderError(
                f"Google Places request failed (HTTP {error.response.status_code})."
            ) from None
        except httpx.HTTPError:
            raise PlaceProviderError("Google Places could not be reached.") from None

        try:
            payload = response.json()
        except ValueError:
            raise PlaceProviderError("Google Places returned invalid JSON.") from None

        if not isinstance(payload, dict) or "error" in payload:
            raise PlaceProviderError("Google Places returned an invalid response.")

        records = payload.get("places", [])
        if not isinstance(records, list):
            raise PlaceProviderError("Google Places returned an invalid places list.")

        retrieved_at = datetime.now(timezone.utc)
        places = []

        try:
            for record in records:
                raw = _GooglePlace.model_validate(record)

                place = Place(
                    place_id=raw.id,
                    name=raw.displayName.text,
                    address=raw.formattedAddress,
                    location=raw.location,
                    source=DataSource(
                        provider="google_places",
                        retrieved_at=retrieved_at,
                        attributions=[
                            Attribution(
                                label=item.provider,
                                url=item.providerUri,
                            )
                            for item in raw.attributions
                        ],
                    ),
                )
                places.append(place)
        except ValidationError:
            raise PlaceProviderError(
                "Google Places returned invalid place data."
            ) from None

        return places