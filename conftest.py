"""Pytest configuration — set environment for test runs."""

import os

# Signal to shared modules that we're running under pytest
# This prevents stdout wrapper conflicts with pytest's capture
os.environ["PYTEST_RUNNING"] = "1"
