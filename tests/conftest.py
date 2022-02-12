import pytest
from src.controller import Controller


@pytest.fixture(scope="function")
def controller():
    controller = Controller()
    yield controller
