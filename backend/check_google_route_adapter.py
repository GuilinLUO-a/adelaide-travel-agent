import httpx

from providers.google_routes import GoogleRoutesProvider
from providers.mock import MockPlaceProvider


def fake_google_response(request):
    return httpx.Response(
        200,
        json={
            "routes": [
                {
                    "distanceMeters": 1400,
                    "duration": "1080s",
                    "warnings": ["Sample route notice."],
                }
            ]
        },
    )


def main():
    places = MockPlaceProvider()

    museum = places.search_places(
        destination="Adelaide",
        category="museums",
    )[0]

    market = places.search_places(
        destination="Adelaide",
        category="food",
    )[0]

    transport = httpx.MockTransport(fake_google_response)

    with httpx.Client(transport=transport) as client:
        provider = GoogleRoutesProvider(
            api_key="test-key",
            client=client,
        )

        route = provider.compute_route(
            origin=museum,
            destination=market,
            from_period="morning",
            to_period="afternoon",
        )

    print(route.model_dump_json(indent=2))


if __name__ == "__main__":
    main()