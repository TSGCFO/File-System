"""
Configuration for pytest that adds custom markers and handling for test dependencies.
"""
import pytest


def pytest_configure(config):
    """Configure custom markers for test filtering."""
    config.addinivalue_line(
        "markers", 
        "expensive: mark a test as requiring significant resources or external dependencies"
    )


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--skip-expensive", 
        action="store_true", 
        default=False,
        help="Skip tests marked as expensive"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle custom options."""
    if config.getoption("--skip-expensive"):
        skip_expensive = pytest.mark.skip(reason="Expensive test skipped with --skip-expensive option")
        for item in items:
            if "expensive" in item.keywords:
                item.add_marker(skip_expensive)