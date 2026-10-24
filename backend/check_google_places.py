import os

import httpx

from providers.base import PlaceProviderError
from providers.google_places import GooglePlacesProvider


def main():
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "")

    if not api_key.strip():
        raise SystemExit("Set GOOGLE_PLACES_API_KEY in this terminal first.")

    try:
        with httpx.Client() as client:
            provider = GooglePlacesProvider(api_key=api_key, client=client)
            places = provider.search_places(
                destination="Adelaide",
                category="museums",
            )
    except PlaceProviderError as error:
        raise SystemExit(str(error)) from None

    print(f"Found {len(places)} place candidates.")

    for place in places:
        print(place.name)
        print(place.address)
        print(f"Place ID: {place.place_id}")
        print()


if __name__ == "__main__":
    main()