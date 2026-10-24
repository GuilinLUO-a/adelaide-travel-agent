from typing import Protocol

from models import ActivityPeriod, Place, Route


class RouteProviderError(RuntimeError):
    """A route provider could not return a valid response."""


class RouteProvider(Protocol):
    def compute_route(
        self,
        *,
        origin: Place,
        destination: Place,
        from_period: ActivityPeriod,
        to_period: ActivityPeriod,
    ) -> Route:
        ...