import pytest


def test_reset(controller):
    controller.parse("mvi a, 0x16")
    controller.parse("mvi b, 0x14")
    controller.run()

    assert str(controller.op.memory_read("A")) == "0x16"
    assert str(controller.op.memory_read("B")) == "0x14"

    controller.reset()
    assert controller.op.super_memory._registers_todict() == {
        "A/PSW": "0x00 0x00",
        "BC": "0x00 0x00",
        "DE": "0x00 0x00",
        "HL": "0x00 0x00",
        "SP": "0xffff",
        "PC": "0x0800",
    }


def test_mvi(controller):
    controller.reset()
    controller.parse("mvi a, 0x12")
    controller.run()
    assert str(controller.op.super_memory.A) == "0x12"
    controller.reset()
    controller.parse("MVI A, 0x14")
    controller.run()
    assert str(controller.op.super_memory.A) == "0x14"
    controller.reset()
    controller.parse("mvi  a,  0x21")
    controller.run()
    assert str(controller.op.super_memory.A) == "0x21"


def test_mov(controller):
    controller.reset()
    controller.parse("mvi a, 0x21")
    controller.parse("mov h, a")
    controller.run()
    assert str(controller.op.super_memory.A) == "0x21"
    assert str(controller.op.super_memory.HL.read("H")) == "0x21"


def test_sta(controller):
    controller.parse("mvi a, 0x24")
    controller.parse("sta 0x0700")
    controller.op.memory_read("0x0700")
    controller.run()
    assert str(controller.op.memory_read("0x0700")) == "0x24"


@pytest.mark.xfail()
def test_db(controller):
    controller.reset()
    _pc_counter = controller.op.super_memory.PC
    controller.parse("db 0x12")
    controller.run()
    assert str(controller.op.memory_read(str(_pc_counter))) == "0x12"


def test_add(controller):
    controller.reset()
    controller.parse("MVI H, 0x26")
    controller.parse("ADD H")
    controller.run()
    assert str(controller.op.memory_read("A")) == "0x26"
    controller.reset_callstack()
    controller.parse("MVI B, 0x44")
    controller.parse("ADD B")
    controller.run()
    assert str(controller.op.memory_read("A")) == "0x6a"


def test_sub(controller):
    controller.reset()
    controller.parse("MVI A, 0x26")
    controller.parse("MVI B, 0xff")
    controller.parse("SUB B")
    controller.run()
    assert str(controller.op.memory_read("A")) == "0x27"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is False
    assert controller.op.flags.CY is True
    assert controller.op.flags.P is True

    controller.reset()
    controller.parse("MVI A, 0x1f")
    controller.parse("MVI B, 0x44")
    controller.parse("SUB B")
    controller.run()
    assert str(controller.op.memory_read("A")) == "0xdb"
    assert controller.op.flags.S is True
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is True
    assert controller.op.flags.P is True
    assert controller.op.flags.CY is True


def test_sbb(controller):
    controller.reset()
    controller.parse("MVI A, 0x1f")
    controller.parse("MVI B, 0xff")
    controller.parse("SBB B")
    controller.run()

    assert str(controller.op.memory_read("A")) == "0x20"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is True
    assert controller.op.flags.P is False
    assert controller.op.flags.CY is True


def test_lxi(controller):
    controller.reset()
    controller.parse("lxi h, 0x1564")
    controller.run()
    assert str(controller.op.memory_read("H")) == "0x15"
    assert str(controller.op.memory_read("L")) == "0x64"


def test_inx(controller):
    controller.reset()
    controller.parse("lxi h, 0x1564")
    controller.parse("inx h")
    controller.run()
    assert str(controller.op.register_pair_read("H")) == "0x1565"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is False
    assert controller.op.flags.P is False
    assert controller.op.flags.CY is False


def test_inr(controller):
    """
    B = 05H --> 06H
    CY=no change | AC=0 | S=0 | P=1 | Z=0
    """
    controller.reset()
    controller.parse("mvi b, 0x05")
    controller.parse("inr b")
    controller.run()
    assert str(controller.op.memory_read("B")) == "0x06"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is False
    assert controller.op.flags.P is True
    assert controller.op.flags.CY is False

    controller.reset()
    controller.parse("mvi b, 0xff")
    controller.parse("inr b")
    controller.run()
    assert str(controller.op.memory_read("B")) == "0x00"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is True
    assert controller.op.flags.AC is True
    assert controller.op.flags.P is True
    assert controller.op.flags.CY is False


def test_dcr(controller):
    """
    B = 45H --> 44H
    CY=no change | AC=0 | S=0 | P=1 | Z=0
    """
    controller.reset()
    controller.parse("dcr b")
    controller.run()
    assert str(controller.op.memory_read("B")) == "0xff"
    assert controller.op.flags.S is True
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is False
    assert controller.op.flags.P is True
    assert controller.op.flags.CY is False

    controller.reset()
    controller.parse("mvi b, 0x45")
    controller.parse("dcr b")
    controller.run()
    assert str(controller.op.memory_read("B")) == "0x44"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is True
    assert controller.op.flags.P is True
    assert controller.op.flags.CY is False


def test_dcx(controller):
    controller.reset()
    controller.parse("lxi h, 0x1564")
    controller.parse("dcx h")
    controller.run()
    assert str(controller.op.register_pair_read("H")) == "0x1563"
    assert controller.op.flags.S is False
    assert controller.op.flags.Z is False
    assert controller.op.flags.AC is False
    assert controller.op.flags.P is False
    assert controller.op.flags.CY is False


def test_lhld(controller):
    controller.reset()
    controller.parse("mvi a, 0x15")
    controller.parse("sta 0x0700")

    controller.parse("mvi a, 0x18")
    controller.parse("sta 0x0701")

    controller.parse("mvi a, 0x00")

    controller.parse("lhld, 0x0700")
    controller.run()
    assert str(controller.op.register_pair_read("H")) == "0x1815"


def test_shld(controller):
    controller.reset()
    controller.parse("lxi h 0x4862")
    controller.parse("shld 0x0700")
    controller.run()

    assert str(controller.op.register_pair_read("H")) == "0x4862"
    assert str(controller.op.memory_read("0x0700")) == "0x62"
    assert str(controller.op.memory_read("0x0701")) == "0x48"


def test_xchg(controller):
    controller.reset()
    controller.parse("lxi h, 0x1815")
    controller.parse("lxi d, 0x2648")
    controller.parse("xchg")
    controller.run()
    assert str(controller.op.register_pair_read("H")) == "0x2648"
    assert str(controller.op.register_pair_read("D")) == "0x1815"


def test_dad(controller):
    controller.reset()
    controller.parse("lxi h, 0xffee")
    controller.parse("lxi d, 0x1248")
    controller.parse("dad d")
    controller.run()

    assert str(controller.op.register_pair_read("H")) == "0x1236"
    assert str(controller.op.register_pair_read("D")) == "0x1248"
    assert controller.op.flags.CY is True

    controller.reset()
    controller.parse("lxi h, 0x4821")
    controller.parse("lxi d, 0x3492")
    controller.parse("dad d")
    controller.run()

    assert str(controller.op.register_pair_read("H")) == "0x7cb3"
    assert str(controller.op.register_pair_read("D")) == "0x3492"
    assert controller.op.flags.CY is False


@pytest.mark.parametrize("mem_acc, carry", [("0x14", True), ("0x18", False)])
def test_jc(controller, mem_acc, carry):
    controller.reset()
    controller.op.flags.CY = carry
    controller.parse("mvi a, 0x14")
    controller.parse("jc down")
    controller.parse("mvi a, 0x18")
    controller.parse("down: mvi b, 0x21")
    controller.run()

    assert str(controller.op.memory_read("A")) == mem_acc
    assert str(controller.op.memory_read("B")) == "0x21"

    memos = [str(x).lower() for x in list(controller.op.memory.values())]
    assert memos == [
        "0x3e",
        "0x14",
        "0xda",
        "0x07",
        "0x08",
        "0x3e",
        "0x18",
        "0x06",
        "0x21",
    ]


@pytest.mark.parametrize("mem_acc, carry", [("0x14", False), ("0x18", True)])
def test_jnc(controller, mem_acc, carry):
    controller.reset()
    controller.op.flags.CY = carry
    controller.parse("mvi a, 0x14")
    controller.parse("jnc down")
    controller.parse("mvi a, 0x18")
    controller.parse("down: mvi b, 0x21")
    controller.run()

    assert str(controller.op.memory_read("A")) == mem_acc
    assert str(controller.op.memory_read("B")) == "0x21"

    memos = [str(x) for x in list(controller.op.memory.values())]
    assert memos == [
        "0x3e",
        "0x14",
        "0xd2",
        "0x07",
        "0x08",
        "0x3e",
        "0x18",
        "0x06",
        "0x21",
    ]


def test_jz(controller):
    controller.reset()
    controller.parse("mvi a, 0x02")
    controller.parse("LOOP: dcr a")
    controller.parse("jnz LOOP")
    controller.run()

    assert str(controller.op.memory_read("A")) == "0x00"
    memo = [str(x).lower() for x in list(controller.op.memory.values())]
    assert memo == ["0x3e", "0x02", "0x3d", "0xc2", "0x02", "0x08"]


@pytest.mark.parametrize(
    "inp, out, in_cy_flag, out_cy_flag",
    [
        ("0x14", "0x28", False, False),
        ("0x14", "0x29", True, False),
        ("0xfa", "0xf4", False, True),
        ("0xfa", "0xf5", True, True),
    ],
)
def test_ral(controller, inp, out, in_cy_flag, out_cy_flag):
    controller.reset()
    controller.op.flags.CY = in_cy_flag
    controller.parse(f"mvi a, {inp}")
    controller.parse("ral")
    controller.run()
    assert str(controller.op.memory_read("A")) == out
    assert controller.op.flags.CY == out_cy_flag


@pytest.mark.parametrize(
    "inp, out, in_cy_flag, out_cy_flag",
    [
        ("0x14", "0x28", False, False),
        ("0x14", "0x28", True, False),
        ("0xfa", "0xf5", False, True),
        ("0xfa", "0xf5", True, True),
    ],
)
def test_rlc(controller, inp, out, in_cy_flag, out_cy_flag):
    controller.reset()
    controller.op.flags.CY = in_cy_flag
    controller.parse(f"mvi a, {inp}")
    controller.parse("rlc")
    controller.run()
    assert str(controller.op.memory_read("A")) == out
    assert controller.op.flags.CY == out_cy_flag
