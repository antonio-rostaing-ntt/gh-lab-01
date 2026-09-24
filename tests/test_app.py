import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))

    yield

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "participants" in response.json()[expected_activity]


def test_signup_for_activity_adds_email(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["participants"]


def test_signup_with_duplicate_email_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in response.json()["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Science Club"
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
