"""E2E tests for file upload via browser and API."""

import os
import tempfile

import pytest
import requests

BASE_URL = "http://localhost:8080"


class TestFileUpload:
    """Tests for file upload functionality."""

    def test_api_ingest_csv_via_requests(self):
        """Upload a CSV file via the /api/ingest endpoint using requests."""
        csv_content = "metric,value\nrevenue,150000\ngrowth,12.5\n"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            with open(csv_path, "rb") as f:
                r = requests.post(
                    f"{BASE_URL}/api/ingest",
                    files={"file": ("data.csv", f, "text/csv")},
                )
            assert r.status_code == 200, f"Upload failed: {r.text}"
            data = r.json()
            assert "job_id" in data
            assert data["status"] == "completed"
            assert "metric_type" in data
            job_id = data["job_id"]

            # Verify result exists
            r2 = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            assert r2.status_code == 200
        finally:
            os.unlink(csv_path)

    def test_result_url_returned(self):
        """After upload, the API returns a result URL or a job_id."""
        r = requests.post(
            f"{BASE_URL}/api/ingest",
            files={"file": ("report.txt", "Quarterly revenue report.\nTotal sales: $2,000,000.\n", "text/plain")},
        )
        assert r.status_code in (200, 422), f"Unexpected status: {r.text}"
        data = r.json()
        # Even when LLM fails, we still get a job_id
        assert "job_id" in data
        # If LLM is available, url is returned; otherwise fallback
        if "url" in data:
            assert data["url"].startswith("/result/")


class TestResultPage:
    """Tests for the result detail page."""

    def test_result_page_rendered(self, page):
        """Result page /result/{id} should render in browser."""
        # Create a job first
        r = requests.post(
            f"{BASE_URL}/api/ingest",
            files={"file": ("kpi.txt", "Employee performance metrics.\nKPI score: 92/100.\n", "text/plain")},
        )
        assert r.status_code == 200
        job_id = r.json()["job_id"]

        # Navigate to result page via browser
        resp = page.goto(f"/result/{job_id}")
        assert resp.status == 200
        assert page.title() != ""

    def test_nonexistent_result_404(self, page):
        """Page for nonexistent job ID should return 404."""
        resp = page.goto("/result/nonexistent_id_12345")
        assert resp.status == 404
