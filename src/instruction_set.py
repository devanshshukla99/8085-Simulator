from src.flags import flags
from src.util import decompose_byte, construct_hex


class Instructions:
    def __init__(self, op) -> None:
        self.op = op
        self._next_link = {"A": "PSW", "B": "C", "D": "E", "H": "L", "S": "P"}
        self._jump_flag = False
        pass

    def _set_opcode(self, func, opcodes):
        return setattr(func.__func__, "opcodes", opcodes)

    def mvi(self, addr, data) -> bool:
        self.op.memory_write(addr, data)
        return True

    def mov(self, to_addr, from_addr) -> bool:
        data = self.op.memory_read(from_addr)
        self.op.memory_write(to_addr, data, log=False)
        return True

    def _next_addr(self, addr):
        return format(int(str(addr), 16) + 1, "#06x")

    def _adder(self, data_1, data_2) -> str:
        # decomposed_data_1 = decompose_byte(data_1, _bytes=1, nibble=True)
        # decomposed_data_2 = decompose_byte(data_2, _bytes=1, nibble=True)

        decomposed_data_1 = decompose_byte(data_1, nibble=True)
        decomposed_data_2 = decompose_byte(data_2, nibble=True)
        _carry, _aux_carry = zip(decomposed_data_1, decomposed_data_2)

        d1, d2 = _aux_carry
        _added_d1_d2_1 = int(d1, 16) + int(d2, 16)
        if _added_d1_d2_1 >= 16:
            _added_d1_d2_1 -= 16
            flags.AC = True

        d1, d2 = _carry
        _added_d1_d2_2 = int(d1, 16) + int(d2, 16)
        if flags.AC:
            _added_d1_d2_2 += 1
        if _added_d1_d2_2 >= 16:
            _added_d1_d2_2 -= 16
            flags.C = True

        return format(_added_d1_d2_2 * 16 + _added_d1_d2_1, "#04x")

    def db(self, *args):
        """
        stores at current location
        """
        print(f"db {args}")
        for x in args:
            self._write_next_PC(x)
        return True

    def add(self, to_addr, from_addr=None) -> bool:
        if not from_addr:
            from_addr = to_addr
            to_addr = "A"
        data_1 = self.op.memory_read(from_addr)
        data_2 = self.op.memory_read(to_addr)
        data = self._adder(data_1, data_2)
        self.op.memory_write(to_addr, data, log=False)
        return True

    def lxi(self, addr, data) -> bool:
        self.op.register_pair_write(addr, data)
        return True

    def inx(self, addr) -> bool:
        data = self.op.register_pair_read(addr)
        data_to_write = format(int(data, 16) + 1, "#06x")
        self.op.register_pair_write(addr, data_to_write, log=False)
        return True

    def inr(self, addr) -> bool:
        data = self.op.memory_read(addr)
        data_to_write = format(int(data, 16) + 1, "#04x")
        self.op.memory_write(addr, data_to_write, log=False)
        return True

    def lhld(self, addr) -> bool:
        data_1 = self.op.memory_read(addr)
        print(f"=========={addr}===========")
        nxt_addr = format(int(addr, 16) + 1, "#06x")
        print(f"=========={nxt_addr}===========")
        data_2 = self.op.memory_read(nxt_addr)
        print(f"=========={data_2}===========")
        self.op.memory_write("H", data_2)
        self.op.memory_write("L", data_1)
        return True

    def xchg(self, *args) -> bool:
        data_1 = self.op.register_pair_read("H")
        data_2 = self.op.register_pair_read("D")
        self.op.register_pair_write("D", data_1)
        self.op.register_pair_write("H", data_2)
        return True

    def dad(self, addr) -> bool:
        data_1 = self.op.register_pair_read(addr)
        data_2 = self.op.register_pair_read("H")
        addition = int(data_1, 16) + int(data_2, 16)
        if addition > int("0xffff", 16):
            raise NotImplementedError("Carry flag not implemented yet!")
        addition = format(addition, "#06x")
        self.op.register_pair_write("H", addition)
        return True

    def sta(self, addr) -> bool:
        data = self.op.memory_read("A")
        self.op.memory_write(addr, data)
        return True

    def jnc(self, jump_flag) -> bool:
        if not flags.C:
            print(jump_flag)
            self._jump_flag = jump_flag
        return True

    def shld(self, addr) -> bool:
        data_1 = self.op.memory_read("H")
        data_2 = self.op.memory_read("L")
        self.op.memory_write(addr, data_2)
        nxt_addr = format(int(addr, 16) + 1, "#6x")
        self.op.memory_write(nxt_addr, data_1)
        return True

    pass
