"""
Playwright E2E test configuration for AutoIngest.

Provides fixtures for browser testing against the running Go server
at http://localhost:3080 (configurable via AUTOINGEST_BASE_URL env var).

Usage:
    pytest tests/e2e/                              # headless
    pytest tests/e2e/ --headed                     # with visible browser
    pytest tests/e2e/ --headed --slowmo 500        # slow-motion debugging
"""

import os
from typing import Generator

import pytest
from playwright.sync_api import BrowserContext, Page

BASE_URL = os.environ.get("AUTOINGEST_BASE_URL", "http://localhost:3080")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Override to inject base_url so page.goto('/') resolves to BASE_URL."""
    return {**browser_context_args, "base_url": BASE_URL}


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a fresh page with base URL configured."""
    pg = context.new_page()
    pg.set_default_timeout(30_000)
    yield pg
