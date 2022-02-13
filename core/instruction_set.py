from core.flags import flags
from core.util import decompose_byte, twos_complement


class Instructions:
    def __init__(self, op) -> None:
        self.op = op
        self._next_link = {"A": "PSW", "B": "C", "D": "E", "H": "L", "S": "P"}
        self._jump_flag = False
        pass

    def _set_opcode(self, func, opcodes):
        return setattr(func.__func__, "opcodes", opcodes)

    def _next_addr(self, addr):
        return format(int(str(addr), 16) + 1, "#06x")

    def _check_flags_and_compute(self, data_1, data_2, add=True):
        og2 = data_2
        if not add:
            data_2 = twos_complement(str(data_2))
        print(data_1, data_2)
        decomposed_data_1 = decompose_byte(data_1, nibble=True)
        decomposed_data_2 = decompose_byte(data_2, nibble=True)
        _carry_data, _aux_data = list(zip(decomposed_data_1, decomposed_data_2))

        if (int(_aux_data[0], 16) + int(_aux_data[1], 16)) >= 16:
            print("AUX FLAG")
            flags.AC = True
        if add:
            if (int(_carry_data[0], 16) + int(_carry_data[1], 16)) >= 16:
                flags.C = True
                print("CARRY FLAG+")
        else:
            if int(str(data_1), 16) < int(str(og2), 16):
                print("CARRY FLAG-")
                flags.C = True
        result = int(str(data_1), 16) + int(str(data_2), 16)
        print(result)
        if result >= 255:
            result -= 256

        result_hex = format(result, "#4x")
        data_bin = format(result, "08b")
        _count_1s = data_bin.count("1")
        if not _count_1s % 2:
            flags.P = True
            print("PARITY")

        print(result, result_hex, data_bin)
        if int(data_bin[0]):
            flags.S = True
            print("SIGN")
        return result_hex

    def mvi(self, addr, data) -> bool:
        self.op.memory_write(addr, data)
        return True

    def mov(self, to_addr, from_addr) -> bool:
        data = self.op.memory_read(from_addr)
        self.op.memory_write(to_addr, data)
        return True

    def sta(self, addr) -> bool:
        data = self.op.memory_read("A")
        self.op.memory_write(addr, data)
        return True

    def db(self, *args):
        """
        stores at current location
        """
        print(f"db {args}")
        for x in args:
            self.op._update_pc(x)
        return True

    def add(self, to_addr, from_addr=None) -> bool:
        if not from_addr:
            from_addr = to_addr
            to_addr = "A"
        from_data = self.op.memory_read(from_addr)
        to_data = self.op.memory_read(to_addr)
        data = self._check_flags_and_compute(from_data, to_data)
        self.op.memory_write(to_addr, data)
        return True

    def sub(self, from_addr, to_addr=None) -> bool:
        if not to_addr:
            to_addr = from_addr
            from_addr = "A"
        to_data = self.op.memory_read(to_addr)
        from_data = self.op.memory_read(from_addr)
        result_data = self._check_flags_and_compute(from_data, to_data, add=False)
        self.op.memory_write(from_addr, result_data)
        return True

    def sbb(self, from_addr, to_addr=None) -> bool:
        if not to_addr:
            to_addr = from_addr
            from_addr = "A"
        to_data = self.op.memory_read(to_addr)
        from_data = self.op.memory_read(from_addr)
        if flags.C:
            flags.C = False
            from_data += 1
        result_data = self._check_flags_and_compute(from_data, to_data, add=False)
        self.op.memory_write(from_addr, result_data)
        return True

    def lxi(self, addr, data) -> bool:
        self.op.register_pair_write(addr, data)
        return True

    def inx(self, addr) -> bool:
        data = self.op.register_pair_read(addr)
        data_to_write = format(int(data, 16) + 1, "#06x")
        self.op.register_pair_write(addr, data_to_write)
        return True

    def inr(self, addr) -> bool:
        data = self.op.memory_read(addr)
        data_to_write = data + 1
        self.op.memory_write(addr, data_to_write)
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

    def jnc(self, jump_flag) -> bool:
        if not flags.C:
            print(jump_flag)
            self._jump_flag = jump_flag
        return True

    def shld(self, addr) -> bool:
        data_1 = self.op.memory_read("H")
        data_2 = self.op.memory_read("L")
        self.op.memory_write(addr, data_2)
        nxt_addr = format(int(addr, 16) + 1, "#06x")
        self.op.memory_write(nxt_addr, data_1)
        return True

    def hlt(self) -> bool:
        raise StopIteration

    pass