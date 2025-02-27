# conftest.py
import pytest
from SimulationModules.TimeDependent.TimeManager import TimeManager
from SimulationModules.RequestHandling.RequestCollector import RequestCollector

@pytest.fixture(autouse=True)
def reset_time_manager(monkeypatch):
    # Reset the singleton instance before each test
    monkeypatch.setattr(TimeManager, "_instance", None)

@pytest.fixture(autouse=True)
def reset_request_collector(monkeypatch):
    # Reset the singleton instance before each test
    monkeypatch.setattr(RequestCollector, "_instance", None)