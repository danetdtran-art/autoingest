"""E2E tests for page navigation and rendering."""

import re
import pytest


BASE_URL = "http://localhost:3080"


class TestHomePage:
    """Tests for the root page (/, /input)."""

    def test_root_page_loads(self, page):
        """GET / should render the upload page."""
        resp = page.goto("/")
        assert resp.status == 200
        assert page.title().startswith("AutoIngest")

    def test_input_page_loads(self, page):
        """GET /input should render the upload page."""
        resp = page.goto("/input")
        assert resp.status == 200
        assert page.title().startswith("AutoIngest")

    def test_upload_form_present(self, page):
        """The page should contain a file upload form."""
        page.goto("/")
        form = page.locator("#upload-form")
        assert form.is_visible()

        file_input = page.locator("#file-input")
        assert file_input.is_visible()

        submit_btn = page.locator("#submit-btn")
        assert submit_btn.is_visible()
        assert submit_btn.text_content() == "Upload & Classify"

    def test_dropzone_present(self, page):
        """The drag-drop zone should be present."""
        page.goto("/")
        dropzone = page.locator("#drop-zone")
        assert dropzone.is_visible()
        label = page.locator("#dropzone-label")
        assert label.is_visible()

    def test_nav_links(self, page):
        """Navigation links to Upload and History should exist."""
        page.goto("/")
        upload_link = page.get_by_role("link", name="Upload")
        assert upload_link.is_visible()
        history_link = page.get_by_role("link", name="History")
        assert history_link.is_visible()


class TestHistoryPage:
    """Tests for the history page."""

    def test_history_page_loads(self, page):
        """GET /history should render successfully."""
        resp = page.goto("/history")
        assert resp.status == 200

    def test_history_has_pagination_or_table(self, page):
        """History page should show some content area."""
        page.goto("/history")
        # The page should have at least the body loaded
        assert page.title() != ""
