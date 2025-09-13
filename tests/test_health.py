import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
    assert "environment" in response.json()

@pytest.mark.parametrize("endpoint", [
    "/docs",
    "/redoc",
    "/api/v1/health"
])
def test_endpoints_are_accessible(endpoint):
    """Test that important endpoints are accessible."""
    response = client.get(endpoint)
    assert response.status_code in [200, 301, 307]  # 301/307 for redirects

def test_invalid_endpoint():
    """Test that an invalid endpoint returns 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
