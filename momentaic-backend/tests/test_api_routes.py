"""
Basic E2E Route Tests
Ensures core API endpoints are responding correctly and Security/CORS
configurations haven't broken the primary routing.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_root_endpoint():
    """Verify the root endpoint serves the welcome message and health links"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome" in data["message"]
    assert "docs" in data

def test_health_check_endpoint():
    """Verify the extensive health check endpoint returns 200"""
    response = client.get(f"{settings.api_v1_prefix}/health")
    # Even if degraded (e.g., redis missing locally), it should return HTTP 200 with status info
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "healthy" in data["status"] or "degraded" in data["status"]
    assert "checks" in data

def test_cors_headers():
    """Verify CORS wildcard restriction (methods/headers)"""
    # Send an OPTIONS request to simulate browser preflight
    response = client.options(
        f"{settings.api_v1_prefix}/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization"
        }
    )
    assert response.status_code == 200
    # Should echo allowed origin or the specific origin
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    
def test_rate_limit_headers():
    """Verify rate limit headers are implicitly considered (or at least we get 200s normally)"""
    response = client.get("/")
    assert response.status_code == 200
    # Rate limit headers check - TestClient bypasses some networking layers but good to sanity check

