import re
from src.memory import Memory, Registers, Byte
from src.flags import flags
from src.exceptions import OPCODENotFound, SyntaxError
from src.util import get_bytes, decompose_byte


class Operations:
    def __init__(self) -> None:
        self.memory = Memory(65535, "0x0000")
        self.registers = Registers()
        self.registers.PC("0x0800")
        self._next_link = {"B": "C", "D": "E", "H": "L", "S": "P"}
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

    def _write_next_PC(self, data):
        self.memory[str(self.registers.PC)] = data
        next(self.registers.PC)
        return True

    def opcode_fetch(self, func, command, *args, **kwargs) -> None:
        print(f"opcode fetch -- {command}")
        command = command.replace(",", "")
        command = command.replace(re.search("0x[0-9a-fA-Z]+", command).group(), "")
        command = command.strip()
        regex = re.compile(command.upper())
        _search_opcode = list(filter(regex.fullmatch, list(func.opcodes.keys())))
        print(_search_opcode)
        if _search_opcode:
            _hex_opcode = func.opcodes.get(_search_opcode[0])
            self._write_next_PC(_hex_opcode)
            return True
        raise OPCODENotFound

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            if addr == "M":
                return self.memory.get(_parsed_addr.read(addr))
            return _parsed_addr.read(addr)
        return self.memory.get(addr)

    def _write_opcode(self, data) -> bool:
        data_bytes = decompose_byte(data)
        for _byte in data_bytes[::-1]:
            print(f"{_byte=}")
            self._write_next_PC(_byte)
        return True

    def memory_write(self, addr, data) -> bool:
        print(f"memory write {addr}|{data}")
        self._write_opcode(data)
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
        self._write_opcode(data)
        _register = self._get_register(addr)
        _register.write_pair(data)
        return True

    pass
