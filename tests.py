import pytest
import json
from api import app

"""
   Sample test data
"""

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_checkHealth(client):
    """
       Tests /api/health
    """
    response = client.get(
        "api/health",
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200


def test_CreateDataInGoRest(client):
    """
       Tests /api/create-entities: create dummy users 
    """
    response = client.post(
        "api/create-entities",
        content_type="application/json")

    assert response.status_code == 200


def test_GetResultsFromLastCreate(client):
    """
       Tests /api/get-entities API: missing scan id
    """
    response = client.get(
        "api/get-entities",
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "scan_id is missing" in data["message"]