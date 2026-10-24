import os

import httpx

from providers.base import PlaceProviderError
from providers.google_places import GooglePlacesProvider
from providers.google_routes import GoogleRoutesProvider
from providers.route_base import RouteProviderError


def main():
    places_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    routes_key = os.environ.get("GOOGLE_ROUTES_API_KEY", "").strip()

    if not places_key or not routes_key:
        raise SystemExit(
            "Set GOOGLE_PLACES_API_KEY and GOOGLE_ROUTES_API_KEY "
            "in this terminal first."
        )

    try:
        with httpx.Client() as client:
            places_provider = GooglePlacesProvider(
                api_key=places_key,
                client=client,
            )

            candidates = places_provider.search_places(
                destination="Adelaide",
                category="museums",
            )

            if len(candidates) < 2:
                raise SystemExit(
                    "The search returned fewer than two places."
                )

            origin, destination = candidates[:2]

            print(f"Origin: {origin.name}")
            print(f"Destination: {destination.name}")

            routes_provider = GoogleRoutesProvider(
                api_key=routes_key,
                client=client,
            )

            route = routes_provider.compute_route(
                origin=origin,
                destination=destination,
                from_period="morning",
                to_period="afternoon",
            )

    except (PlaceProviderError, RouteProviderError) as error:
        raise SystemExit(str(error)) from None

    print(route.model_dump_json(indent=2))


if __name__ == "__main__":
    main()