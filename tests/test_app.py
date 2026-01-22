"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test cases for /activities endpoint"""

    def test_get_activities_returns_list(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Test cases for /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]

    def test_signup_duplicate_fails(self):
        """Test that duplicate signup fails"""
        email = "duplicate@test.com"
        activity = "Programming%20Class"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Duplicate signup should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup to nonexistent activity fails"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_adds_participant(self):
        """Test that signup adds participant to activity"""
        email = "newparticipant@test.com"
        activity = "Tennis%20Club"
        
        # Get activities before signup
        response_before = client.get("/activities")
        data_before = response_before.json()
        participants_before = data_before["Tennis Club"]["participants"].copy()
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Get activities after signup
        response_after = client.get("/activities")
        data_after = response_after.json()
        participants_after = data_after["Tennis Club"]["participants"]
        
        # Verify participant was added
        assert email in participants_after
        assert len(participants_after) == len(participants_before) + 1


class TestUnregisterEndpoint:
    """Test cases for /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from activity"""
        email = "unregister@test.com"
        activity = "Drama%20Club"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test unregister from nonexistent activity fails"""
        response = client.delete(
            "/activities/NonExistent/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_nonexistent_participant_fails(self):
        """Test unregister of non-registered participant fails"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@test.com"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        email = "removetest@test.com"
        activity = "Debate%20Team"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant was added
        response_before = client.get("/activities")
        data_before = response_before.json()
        assert email in data_before["Debate Team"]["participants"]
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Verify participant was removed
        response_after = client.get("/activities")
        data_after = response_after.json()
        assert email not in data_after["Debate Team"]["participants"]


class TestRootEndpoint:
    """Test cases for root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
