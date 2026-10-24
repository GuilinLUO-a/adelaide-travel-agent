from datetime import datetime, timezone

from models import ActivityPeriod, DataSource, Place, Route


class MockRouteProvider:
    def compute_route(
        self,
        *,
        origin: Place,
        destination: Place,
        from_period: ActivityPeriod,
        to_period: ActivityPeriod,
    ) -> Route:
        return Route(
            from_period=from_period,
            to_period=to_period,
            from_place_id=origin.place_id,
            to_place_id=destination.place_id,
            travel_mode="walking",
            status="available",
            distance_meters=1400,
            duration_seconds=1080,
            is_estimate=True,
            encoded_polyline=None,
            source=DataSource(
                provider="mock",
                retrieved_at=datetime.now(timezone.utc),
            ),
        )