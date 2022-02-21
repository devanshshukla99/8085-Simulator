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
    controller.parse("db 0x12")
    controller.run()
    assert str(controller.op.memory_read(controller.op.super_memory.PC - 1)) == "0x12"


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


def test_inr(controller):
    controller.reset()
    controller.parse("mvi b, 0x15")
    controller.parse("inr b")
    controller.run()
    assert str(controller.op.memory_read("B")) == "0x16"


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

    print(controller.inspect())


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


def test_jnc_nocarry(controller):
    controller.reset()
    controller.op.flags.CY = False
    controller.parse("mvi a, 0x14")
    controller.parse("jnc down")
    controller.parse("mvi a, 0x18")
    controller.parse("down: mvi b, 0x21")
    controller.run()

    assert str(controller.op.memory_read("A")) == "0x14"
    assert str(controller.op.memory_read("B")) == "0x21"


def test_jnc_carry(controller):
    controller.reset()
    controller.op.flags.CY = True
    controller.parse("mvi a, 0x14")
    controller.parse("jnc down")
    controller.parse("mvi a, 0x18")
    controller.parse("down: mvi b, 0x21")
    controller.run()

    assert str(controller.op.memory_read("A")) == "0x18"
    assert str(controller.op.memory_read("B")) == "0x21"


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
