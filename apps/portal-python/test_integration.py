"""
Integration tests for the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_graphql_endpoint_exists(self, client):
        """Test that GraphQL endpoint is accessible."""
        response = client.get("/graphql")
        assert response.status_code == 200


class TestFileUpload:
    """Test file upload endpoints."""

    def test_upload_resume_txt(self, client):
        """Test uploading a text resume."""
        files = {"file": ("resume.txt", b"Sample resume content", "text/plain")}
        response = client.post("/api/upload/resume", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "resume.txt"
        assert data["size"] > 0
        assert data["content_type"] == "text/plain"

    def test_upload_invalid_file_type(self, client):
        """Test uploading an invalid file type."""
        files = {"file": ("file.exe", b"Invalid content", "application/x-msdownload")}
        response = client.post("/api/upload/resume", files=files)
        assert response.status_code == 400

    def test_upload_job_description(self, client):
        """Test uploading a job description."""
        files = {"file": ("job.txt", b"Senior Engineer\nTechCorp\nJob details...", "text/plain")}
        response = client.post("/api/upload/job-description", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "parsed" in data
        assert data["parsed"]["title"]


class TestGraphQLAPI:
    """Test GraphQL queries and mutations."""

    def test_modules_query(self, client):
        """Test querying available modules."""
        query = """
        query {
            modules {
                id
                name
                status
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "modules" in data["data"]
        assert len(data["data"]["modules"]) > 0

    def test_applications_query(self, client):
        """Test querying job applications."""
        query = """
        query {
            applications {
                id
                jobTitle
                company
                status
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "applications" in data["data"]

    def test_match_resume_mutation(self, client):
        """Test resume matching mutation."""
        mutation = """
        mutation {
            matchResume(input: {
                resumeText: "Python developer with 5 years experience"
                jobDescription: "Looking for Python developer with distributed systems experience"
            }) {
                overallScore
                keywordMatch
                suggestions
            }
        }
        """
        response = client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "matchResume" in data["data"]
        score_data = data["data"]["matchResume"]
        assert score_data["overallScore"] >= 0
        assert isinstance(score_data["suggestions"], list)


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
        # CORS headers should be present on actual requests
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling."""

    def test_404_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_graphql_query(self, client):
        """Test invalid GraphQL query handling."""
        query = """
        query {
            invalidQuery {
                field
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        # Should return 200 with GraphQL errors
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
