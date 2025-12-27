"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {}
    for name, data in activities.items():
        original_activities[name] = {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
    
    yield
    
    # Restore original state after test
    for name, data in original_activities.items():
        activities[name]["participants"] = data["participants"].copy()


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client):
        """Test that signing up twice with same email returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_already_registered_user(self, client):
        """Test that existing participant cannot sign up again"""
        # Try to sign up with an email already in the participants list
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Math%20Olympiad/signup?email=mathwhiz@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Math Olympiad" in data["message"]


class TestIntegration:
    """Integration tests"""
    
    def test_full_signup_workflow(self, client):
        """Test complete workflow: view activities -> signup -> verify"""
        # Step 1: Get all activities
        activities_response = client.get("/activities")
        assert activities_response.status_code == 200
        activities_data = activities_response.json()
        
        # Step 2: Choose an activity and sign up
        activity_name = "Drama Club"
        original_count = len(activities_data[activity_name]["participants"])
        
        email = "newcomer@mergington.edu"
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Step 3: Verify the signup by fetching activities again
        updated_activities = client.get("/activities")
        updated_data = updated_activities.json()
        new_count = len(updated_data[activity_name]["participants"])
        
        assert new_count == original_count + 1
        assert email in updated_data[activity_name]["participants"]
