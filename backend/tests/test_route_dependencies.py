import pytest
from fastapi import HTTPException

from dependencies import get_route_provider
from providers.google_routes import GoogleRoutesProvider
from providers.mock_routes import MockRouteProvider


def test_default_route_provider_is_mock(monkeypatch):
    monkeypatch.delenv("ROUTE_PROVIDER", raising=False)
    dependency = get_route_provider()

    try:
        assert isinstance(next(dependency), MockRouteProvider)
    finally:
        dependency.close()


def test_google_route_provider_can_be_selected(monkeypatch):
    monkeypatch.setenv("ROUTE_PROVIDER", "google_routes")
    monkeypatch.setenv("GOOGLE_ROUTES_API_KEY", "test-routes-key")
    dependency = get_route_provider()

    try:
        assert isinstance(next(dependency), GoogleRoutesProvider)
    finally:
        dependency.close()


def test_unknown_route_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("ROUTE_PROVIDER", "unknown")

    with pytest.raises(HTTPException) as caught:
        next(get_route_provider())

    assert caught.value.status_code == 503
    assert "ROUTE_PROVIDER" in caught.value.detail


def test_google_route_provider_requires_key(monkeypatch):
    monkeypatch.setenv("ROUTE_PROVIDER", "google_routes")
    monkeypatch.delenv("GOOGLE_ROUTES_API_KEY", raising=False)

    with pytest.raises(HTTPException) as caught:
        next(get_route_provider())

    assert caught.value.status_code == 503
    assert "GOOGLE_ROUTES_API_KEY" in caught.value.detail