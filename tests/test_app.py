
import pytest
from app import app, initialize_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_tasks.db"
    monkeypatch.setattr("app.DATABASE", str(test_db))

    initialize_db()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_add_task(client):
    client.post("/add", data={"title": "Learn Docker"})
    response = client.get("/")
    assert b"Learn Docker" in response.data


def test_update_task(client):
    client.post("/add", data={"title": "Learn AWS"})
    client.get("/update/1")
    response = client.get("/")
    assert b"Completed" in response.data


def test_delete_task(client):
    client.post("/add", data={"title": "Learn Terraform"})
    client.get("/delete/1")
    response = client.get("/")
    assert b"Learn Terraform" not in response.data
