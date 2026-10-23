from typing import Protocol

from models import Place


class PlaceProvider(Protocol):
    def search_places(
        self,
        *,
        destination: str,
        category: str,
    ) -> list[Place]:
        ...