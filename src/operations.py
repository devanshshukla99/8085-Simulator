from src.util import decompose_byte, construct_hex
from src.memory import Memory, Registers, Byte
from src.flags import flags
from src.exceptions import SyntaxError


class Operations:
    def __init__(self) -> None:
        self.memory = Memory(4096, "0x0000")
        self.registers = Registers()
        self._next_link = {"B": "C", "D": "E", "H": "L", "S": "P"}
        # self._registers_list = ["A", "PSW", "B", "C", "D", "E", "H", "L", "S", "P", "PC"]
        self._registers_list = {
            "A": self.registers.A,
            "PSW": self.registers.PSW,
            "B": self.registers.BC,
            "C": self.registers.BC,
            "D": self.registers.DE,
            "E": self.registers.DE,
            "H": self.registers.HL,
            "L": self.registers.HL,
            "S": self.registers.SP,
            "P": self.registers.SP,
            "PC": self.registers.PC,
        }
        # self._registers_list["M"] = self.memory[self._callback_register_M()]
        pass

    def inspect(self):
        return "\n\n".join([self.registers.inspect(), flags.inspect(), str(self.memory)])

    def _parse_addr(self, addr):
        print(f"_parse_addr {self._registers_list.get(addr, None)}")
        return self._registers_list.get(addr, None)

    def _callback_register_M(self):
        return self.register_pair_read("H")

    def opcode_fetch(self, opcode) -> None:
        print(f"opcode fetch -- {opcode}")
        pass

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.read(addr)
        return self.memory.get(addr)

    def memory_write(self, addr, data) -> bool:
        print(f"memory write {addr}|{data}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.write(data, addr)
        self.memory[addr] = data
        return True

    def register_pair_read(self, addr) -> Byte:
        print(f"register pair read {addr}")
        if nxt_addr := self._next_link.get(addr, None):
            data_1 = self._parse_addr(addr).read()
            data_2 = self._parse_addr(nxt_addr).read()
            print(data_1, data_2)
            return construct_hex(data_1, data_2)
        raise SyntaxError(msg="next link not found; check the instruction")

    def register_pair_write(self, addr, data) -> bool:
        print(f"register pair write {addr}|{data}")
        if nxt_addr := self._next_link.get(addr, None):
            data_to_write = decompose_byte(data, _bytes=2)
            print(data_to_write)
            self._parse_addr(addr).write(data_to_write[0])
            self._parse_addr(nxt_addr).write(data_to_write[1])
            return True
        raise SyntaxError(msg="next link not found; check the instruction")

    pass
