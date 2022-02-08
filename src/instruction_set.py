from src.flags import flags
from src.util import decompose_byte
from src.exceptions import SyntaxError


class Instructions:
    def __init__(self, op) -> None:
        self.op = op
        self._next_link = {"A": "PSW", "B": "C", "D": "E", "H": "L", "S": "P"}
        pass

    def mvi(self, to_addr, from_addr) -> None:
        data = self.op.memory_read(from_addr)
        self.op.memory_write(to_addr, data)
        return

    def _adder(self, data_1, data_2):
        decomposed_data_1 = decompose_byte(data_1, mem_size=4)
        decomposed_data_2 = decompose_byte(data_2, mem_size=4)
        _carry, _aux_carry = zip(decomposed_data_1, decomposed_data_2)

        d1, d2 = _aux_carry
        _added_d1_d2_1 = int(d1, 16) + int(d2, 16)
        if _added_d1_d2_1 >= 16:
            _added_d1_d2_1 -= 16
            flags.AC = True

        d1, d2 = _carry
        _added_d1_d2_2 = int(d1, 16) + int(d2, 16)
        if _added_d1_d2_2 >= 16:
            _added_d1_d2_2 -= 16
            flags.C = True

        return format(_added_d1_d2_2 * 16 + _added_d1_d2_1, "#04x")

    def add(self, to_addr, from_addr=None):
        if not from_addr:
            from_addr = to_addr
            to_addr = "A"
        data_1 = self.op.memory_read(from_addr)
        data_2 = self.op.memory_read(to_addr)
        data = self._adder(data_1, data_2)
        self.op.memory_write(to_addr, data)
        return

    def lxi(self, to_addr, data) -> None:
        data_to_write = decompose_byte(data)
        if not data_to_write:
            raise ValueError(f"byte by byte failed {data_to_write}")
        self.op.memory_write(to_addr, data_to_write[0])
        if nxt_to_addr := self._next_link.get(to_addr, None):
            self.op.memory_write(nxt_to_addr, data_to_write[1])
            return
        raise SyntaxError(msg="next link not found; check the instruction")

    pass
