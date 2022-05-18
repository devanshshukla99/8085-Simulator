import pytest

from core.flags import Flags


@pytest.fixture(scope="function")
def flags():
    _flags = Flags()
    yield _flags


def test_flags_todict(flags):
    assert flags.todict() == {
        "CY": False,
        "P": False,
        "AC": False,
        "Z": False,
        "S": False,
    }


def test_flags_items(flags):
    assert flags.items() == flags._flags.items()


def test_flags_set_flags(flags):
    assert all(flags._flags.values()) is False
    new_flags = {
        "CY": True,
        "P": True,
        "AC": True,
        "Z": True,
        "S": True,
    }
    flags.set_flags(new_flags)
    assert all(flags._flags.values())


def test_flags_setitem(flags):
    assert all(flags._flags.values()) is False
    flags["CY"] = True
    flags["P"] = True
    assert flags.todict() == {
        "CY": True,
        "P": True,
        "AC": False,
        "Z": False,
        "S": False,
    }


def test_flags_reset(flags):
    assert all(flags._flags.values()) is False
    flags.CY = True
    flags.P = True
    assert flags.todict() == {
        "CY": True,
        "P": True,
        "AC": False,
        "Z": False,
        "S": False,
    }
    flags.reset()
    assert all(flags._flags.values()) is False
