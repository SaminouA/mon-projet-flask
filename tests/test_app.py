import pytest
from src.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"

def test_hello(client):
    response = client.get("/hello/Alice")
    assert response.status_code == 200
    assert "Alice" in response.get_json()["message"]

def test_not_found(client):
    response = client.get("/page-inexistante")
    assert response.status_code == 404

def test_add(client):
    response = client.get("/add/3/5")
    assert response.status_code == 200
    assert response.get_json()["result"] == 8
    
def test_add_negative(client):
    response = client.get("/add/-1/1")
    assert response.get_json()["result"] == 0