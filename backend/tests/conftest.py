import pytest


@pytest.fixture(autouse=True)
def use_mock_places_by_default(monkeypatch):
    monkeypatch.setenv("PLACE_PROVIDER", "mock")
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    monkeypatch.setenv("ROUTE_PROVIDER", "mock")
    monkeypatch.delenv("GOOGLE_ROUTES_API_KEY", raising=False)
