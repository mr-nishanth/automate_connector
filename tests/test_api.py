"""Tests for the FastAPI server endpoints."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def reset_items() -> Iterator[None]:
    store.reset_store()
    yield
    store.reset_store()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_root_returns_welcome(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_items_returns_seeded_items(client: TestClient) -> None:
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert {"id", "name", "description", "price"} <= set(items[0])


def test_get_item_by_valid_id(client: TestClient) -> None:
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Widget"


def test_get_item_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/items/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_get_item_non_integer_id_returns_422(client: TestClient) -> None:
    response = client.get("/api/v1/items/abc")
    assert response.status_code == 422


def test_create_item_then_retrieve(client: TestClient) -> None:
    payload = {"name": "Thing", "description": "New thing", "price": 3.5}
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Thing"
    assert created["price"] == 3.5
    assert isinstance(created["id"], int)

    fetched = client.get(f"/api/v1/items/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_create_item_without_description(client: TestClient) -> None:
    response = client.post("/api/v1/items", json={"name": "Plain", "price": 0})
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_item_missing_name_returns_422(client: TestClient) -> None:
    response = client.post("/api/v1/items", json={"price": 1.0})
    assert response.status_code == 422


def test_create_item_negative_price_returns_422(client: TestClient) -> None:
    response = client.post("/api/v1/items", json={"name": "Bad", "price": -1})
    assert response.status_code == 422


def test_create_item_empty_name_returns_422(client: TestClient) -> None:
    response = client.post("/api/v1/items", json={"name": "", "price": 1})
    assert response.status_code == 422
