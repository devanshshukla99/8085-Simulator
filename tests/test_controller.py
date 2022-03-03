import pytest


@pytest.mark.parametrize(
    "val, result",
    [
        ("mvi a, 0x12", ("MVI", ["a", "0x12"], {})),
        ("lxi h, 0x1fc2", ("LXI", ["h", "0x1fc2"], {})),
        ("JC ZO", ("JC", ["ZO"], {})),
        ("DCR b", ("DCR", ["b"], {})),
    ],
)
def test_controller_parser(controller, val, result):
    assert controller._parser(val) == result


@pytest.mark.parametrize(
    "val, result",
    [
        ("mvi a, 0x12", {"0x0800": "0x3e", "0x0801": "0x12"}),
        ("lxi h, 0x1fc2", {"0x0800": "0x21", "0x0801": "0xc2", "0x0802": "0x1f"}),
        (
            "JC ZO",
            {"0x0800": "0xda", "0x0801": "0xff", "0x0802": "0xff"},
        ),  # 0x0801 and 0x0802 should currently have placeholders in them
        ("DCR b", {"0x0800": "0x05"}),
    ],
)
def test_controller_parse(controller, val, result):
    assert controller.parse(val)
    _memory = controller.op.memory
    _str_memory = {}
    for key, value in _memory.items():
        _str_memory[key] = str(value)
    assert _str_memory == result


@pytest.mark.parametrize("flag_key, flag_val", [("CY", True), ("P", True), ("AC", True), ("S", True), ("P", True)])
def test_controller_set_flag(controller, flag_key, flag_val):
    controller.reset()
    assert controller.set_flag(flag_key, flag_val)
    assert controller.op.flags[flag_key] is flag_val


def test_controller_run_once(controller):
    controller.parse("mvi a, 0x12")
    controller.parse("mvi b, 0x14")

    assert controller.run_once()
    assert str(controller.op.memory_read("A")) == "0x12"
    assert str(controller.op.memory_read("B")) == "0x00"

    assert controller.run_once()
    assert str(controller.op.memory_read("A")) == "0x12"
    assert str(controller.op.memory_read("B")) == "0x14"

    assert not controller.run_once()
