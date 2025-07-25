import pytest
from app.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_home_endpoint(client, monkeypatch):
    # Mock the external request to avoid calling the real IP API during tests
    def mock_get(*args, **kwargs):
        class MockResponse:
            text = "123.456.789.0"
        return MockResponse()
    
    monkeypatch.setattr("requests.get", mock_get)

    response = client.get("/")
    assert response.status_code == 200
    assert "My public IP is: 123.456.789.0" in response.get_data(as_text=True)
