from fastapi.testclient import TestClient


def test_list_items(client: TestClient) -> None:
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_create_item(client: TestClient) -> None:
    payload = {"title": "New Test Item", "description": "Created during pytest"}
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert "id" in data


def test_get_item_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404
