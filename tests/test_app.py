import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity in data
    assert data[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Math Club"
    new_email = "newstudent@mergington.edu"
    assert new_email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_activity_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email_to_remove = app_module.activities[activity_name]["participants"][0]
    assert email_to_remove in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email_to_remove}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Drama Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
