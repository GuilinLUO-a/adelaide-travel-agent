import json

from providers.google_routes import build_walking_route_request
from providers.mock import MockPlaceProvider


def main():
    place_provider = MockPlaceProvider()

    museum = place_provider.search_places(
        destination="Adelaide",
        category="museums",
    )[0]

    market = place_provider.search_places(
        destination="Adelaide",
        category="food",
    )[0]

    request_body = build_walking_route_request(
        origin=museum,
        destination=market,
    )

    print(json.dumps(request_body, indent=2))


if __name__ == "__main__":
    main()