from datetime import datetime, timezone

import httpx
from pydantic import Field, ValidationError

from models import ActivityPeriod, AppModel, DataSource, Place, Route
from providers.route_base import RouteProviderError


ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

ROUTE_FIELD_MASK = ",".join([
    "routes.distanceMeters",
    "routes.duration",
    "routes.polyline.encodedPolyline",
    "routes.warnings",
])


def build_walking_route_request(
    *,
    origin: Place,
    destination: Place,
) -> dict:
    return {
        "origin": {
            "location": {
                "latLng": origin.location.model_dump(),
            },
        },
        "destination": {
            "location": {
                "latLng": destination.location.model_dump(),
            },
        },
        "travelMode": "WALK",
        "computeAlternativeRoutes": False,
        "polylineEncoding": "ENCODED_POLYLINE",
        "languageCode": "en-AU",
        "units": "METRIC",
    }
    
WALKING_NOTICE = (
    "Google walking routes are in beta and may omit sidewalks or pedestrian paths."
)


class _GooglePolyline(AppModel):
    encodedPolyline: str = ""


class _GoogleRouteData(AppModel):
    distanceMeters: int = Field(default=0, ge=0, strict=True)
    duration: str = Field(pattern=r"^[0-9]+(?:\.[0-9]{1,9})?s$")
    polyline: _GooglePolyline | None = None
    warnings: list[str] = Field(default_factory=list)
    
class GoogleRoutesProvider:
    def __init__(self, *, api_key: str, client: httpx.Client):
        if not api_key.strip():
            raise RouteProviderError("Google Routes API key is not configured.")

        self._api_key = api_key.strip()
        self._client = client

    def compute_route(
        self,
        *,
        origin: Place,
        destination: Place,
        from_period: ActivityPeriod,
        to_period: ActivityPeriod,
    ) -> Route:
        empty_route = Route(
            from_period=from_period,
            to_period=to_period,
            from_place_id=origin.place_id,
            to_place_id=destination.place_id,
            status="not_found",
        )

        request_body = build_walking_route_request(
            origin=origin,
            destination=destination,
        )

        try:
            response = self._client.post(
                ROUTES_URL,
                headers={
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": ROUTE_FIELD_MASK,
                },
                json=request_body,
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise RouteProviderError(
                f"Google Routes request failed (HTTP {error.response.status_code})."
            ) from None
        except httpx.HTTPError:
            raise RouteProviderError("Google Routes could not be reached.") from None

        try:
            payload = response.json()
        except ValueError:
            raise RouteProviderError("Google Routes returned invalid JSON.") from None

        if not isinstance(payload, dict) or "error" in payload:
            raise RouteProviderError("Google Routes returned an invalid response.")

        routes = payload.get("routes", [])

        if not isinstance(routes, list):
            raise RouteProviderError("Google Routes returned an invalid routes list.")

        if not routes:
            return empty_route

        try:
            raw = _GoogleRouteData.model_validate(routes[0])
            duration_seconds = float(raw.duration[:-1])

            encoded_polyline = None
            if raw.polyline is not None:
                encoded_polyline = raw.polyline.encodedPolyline or None

            return Route(
                from_period=from_period,
                to_period=to_period,
                from_place_id=origin.place_id,
                to_place_id=destination.place_id,
                travel_mode="walking",
                status="available",
                distance_meters=raw.distanceMeters,
                duration_seconds=duration_seconds,
                is_estimate=True,
                encoded_polyline=encoded_polyline,
                source=DataSource(
                    provider="google_routes",
                    retrieved_at=datetime.now(timezone.utc),
                ),
                warnings=[WALKING_NOTICE] + raw.warnings,
            )
        except ValidationError:
            raise RouteProviderError(
                "Google Routes returned invalid route data."
            ) from None