import pytest

from core.controller import Controller


@pytest.fixture(scope="function")
def controller():
    controller = Controller()
    yield controller
