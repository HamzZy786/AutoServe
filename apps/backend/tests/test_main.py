import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_database
from models import User

# Test client
client = TestClient(app)

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock()
    return db

@pytest.fixture
def override_get_db(mock_db):
    """Override the get_database dependency"""
    def _override_get_db():
        return mock_db
    
    app.dependency_overrides[get_database] = _override_get_db
    yield
    app.dependency_overrides = {}

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_ready_check(self):
        """Test readiness check"""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

class TestMetricsEndpoints:
    """Test metrics endpoints"""
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
        assert "http_request_duration_seconds" in response.text
    
    def test_metrics_json(self):
        """Test JSON metrics endpoint"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "application" in data

class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_create_user(self, override_get_db, mock_db):
        """Test user creation"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # Mock the database operations
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_user = User(id=1, **user_data)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data  # Password should not be returned
    
    def test_create_duplicate_user(self, override_get_db, mock_db):
        """Test creating user with duplicate email"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # Mock existing user
        mock_db.query.return_value.filter.return_value.first.return_value = User(id=1, **user_data)
        
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_users(self, override_get_db, mock_db):
        """Test getting list of users"""
        mock_users = [
            User(id=1, username="user1", email="user1@example.com"),
            User(id=2, username="user2", email="user2@example.com")
        ]
        mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
        
        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "user1"

class TestTaskEndpoints:
    """Test task management endpoints"""
    
    @patch('main.process_data_task.delay')
    def test_create_task(self, mock_task):
        """Test task creation"""
        mock_task.return_value.id = "test-task-id"
        
        task_data = {"data": "test data", "priority": "high"}
        response = client.post("/api/tasks/", json=task_data)
        
        assert response.status_code == 202
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "pending"
    
    def test_get_task_status(self):
        """Test getting task status"""
        task_id = "test-task-id"
        
        with patch('main.AsyncResult') as mock_result:
            mock_result.return_value.status = "SUCCESS"
            mock_result.return_value.result = {"processed": True}
            
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, override_get_db, mock_db):
        """Test successful login"""
        from auth import verify_password, get_password_hash
        
        password = "testpassword123"
        hashed_password = get_password_hash(password)
        user = User(id=1, username="testuser", email="test@example.com", password_hash=hashed_password)
        
        mock_db.query.return_value.filter.return_value.first.return_value = user
        
        login_data = {"username": "testuser", "password": password}
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, override_get_db, mock_db):
        """Test login with invalid credentials"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        login_data = {"username": "nonexistent", "password": "wrongpassword"}
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON data"""
        response = client.post(
            "/api/users/",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoints"""
    
    async def test_async_health_check(self):
        """Test async health check"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
    
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            tasks = [ac.get("/health") for _ in range(10)]
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
