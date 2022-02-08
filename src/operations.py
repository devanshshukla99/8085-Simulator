from src.util import decompose_byte, construct_hex
from src.memory import Memory, Registers, Byte
from src.flags import flags
from src.exceptions import SyntaxError


class Operations:
    def __init__(self) -> None:
        self.memory = Memory(65535, "0x0000")
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
            "M": self.registers.M,
        }
        pass

    def inspect(self):
        return "\n\n".join([self.registers.inspect(), flags.inspect(), str(self.memory)])

    def _parse_addr(self, addr):
        addr = addr.upper()
        print(f"_parse_addr {self._registers_list.get(addr, None)}")
        return self._registers_list.get(addr, None)

    def _get_register(self, addr):
        addr = addr.upper()
        if _register := self._registers_list.get(addr, None):
            return _register
        raise SyntaxError(msg="next link not found; check the instruction")

    def opcode_fetch(self, opcode) -> None:
        print(f"opcode fetch -- {opcode}")
        pass

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            if addr == "M":
                return self.memory.get(_parsed_addr.read(addr))
            return _parsed_addr.read(addr)
        return self.memory.get(addr)

    def memory_write(self, addr, data) -> bool:
        print(f"memory write {addr}|{data}")
        if _parsed_addr := self._parse_addr(addr):
            if addr == "M":
                self.memory_write(self.memory_read("M"), data)
                return True
            return _parsed_addr.write(data, addr)
        self.memory[addr] = data
        return True

    def register_pair_read(self, addr) -> Byte:
        print(f"register pair read {addr}")
        _register = self._get_register(addr)
        return _register.read_pair()

    def register_pair_write(self, addr, data) -> bool:
        print(f"register pair write {addr}|{data}")
        _register = self._get_register(addr)
        _register.write_pair(data)
        return True

    pass
