from typing import Protocol

from models import Place


class PlaceProviderError(RuntimeError):
    """A place provider could not return a valid response."""


class PlaceProvider(Protocol):
    def search_places(
        self,
        *,
        destination: str,
        category: str,
    ) -> list[Place]:
        ...