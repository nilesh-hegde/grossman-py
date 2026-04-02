"""Pytest configuration — register custom markers."""


def pytest_configure(config):
    config.addinivalue_line("markers", "online: requires network access")
    config.addinivalue_line("markers", "slow: downloads all 20 datasets")
