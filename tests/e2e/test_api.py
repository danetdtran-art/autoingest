"""E2E tests for API endpoints."""

import pytest
import requests

BASE_URL = "http://localhost:3080"


def create_job(filename="test.txt", content="Test document.\nRevenue: $100,000.\n"):
    """Helper: create a job via the ingest API, return the parsed JSON."""
    r = requests.post(
        f"{BASE_URL}/api/ingest",
        files={"file": (filename, content, "text/plain")},
    )
    assert r.status_code == 200, f"Failed to create job: {r.text}"
    return r.json()


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, context):
        """GET /health should return status ok."""
        response = context.request.get(f"{BASE_URL}/health")
        assert response.status == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_valid_json(self, context):
        """The health response should parse as valid JSON."""
        response = context.request.get(f"{BASE_URL}/health")
        assert response.status == 200
        data = response.json()
        assert "status" in data


class TestApiIngest:
    """Tests for the /api/ingest endpoint."""

    def test_ingest_missing_file(self, context):
        """POST /api/ingest without a file should return 400."""
        response = context.request.post(
            f"{BASE_URL}/api/ingest",
            data={},
        )
        assert response.status == 400
        data = response.json()
        assert "error" in data

    def test_ingest_txt_file(self):
        """POST /api/ingest with a TXT file should succeed."""
        r = requests.post(
            f"{BASE_URL}/api/ingest",
            files={"file": ("doc.txt", "Test document for classification.\nRevenue: $500,000.\n", "text/plain")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "job_id" in data
        assert data["status"] == "completed"
        assert "metric_type" in data
        assert "confidence" in data

    def test_ingest_csv_file(self):
        """POST /api/ingest with a CSV file should succeed."""
        r = requests.post(
            f"{BASE_URL}/api/ingest",
            files={"file": ("data.csv", "name,value\nsales,100000\nprofit,25000\n", "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "job_id" in data
        assert data["status"] == "completed"


class TestApiJobs:
    """Tests for the /api/jobs/{id} endpoint."""

    def test_get_job_not_found(self, context):
        """GET /api/jobs/nonexistent should return 404."""
        response = context.request.get(f"{BASE_URL}/api/jobs/nonexistent_id")
        assert response.status == 404

    def test_get_existing_job(self):
        """After creating a job, it should be retrievable."""
        job_info = create_job(content="Test job document.\nRevenue: $100,000.\n")
        job_id = job_info["job_id"]

        r = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        assert r.status_code == 200
        job_data = r.json()
        # SQLite returns lowercase column names via Go's encoding/json
        assert job_data["id"] == job_id
        assert "file_name" in job_data


class TestApiResults:
    """Tests for the /api/results endpoint."""

    def test_list_results(self, context):
        """GET /api/results should return results list."""
        response = context.request.get(f"{BASE_URL}/api/results")
        assert response.status == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
