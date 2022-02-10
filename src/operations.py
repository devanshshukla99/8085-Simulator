import re
from src.memory import Memory, Registers, Byte, SuperMemory
from src.flags import flags
from src.exceptions import OPCODENotFound, SyntaxError
from src.util import get_bytes, decompose_byte


class Operations:
    def __init__(self) -> None:
        self.super_memory = SuperMemory()
        self.memory = self.super_memory.memory
        self.super_memory.PC("0x0800")
        self._registers_list = {
            "A": self.super_memory.A,
            "PSW": self.super_memory.PSW,
            "B": self.super_memory.BC,
            "C": self.super_memory.BC,
            "D": self.super_memory.DE,
            "E": self.super_memory.DE,
            "H": self.super_memory.HL,
            "L": self.super_memory.HL,
            "S": self.super_memory.SP,
            "P": self.super_memory.SP,
            "PC": self.super_memory.PC,
            "M": self.super_memory.M,
        }
        pass

    def inspect(self):
        return "\n\n".join([flags.inspect(), self.super_memory.inspect()])

    def _parse_addr(self, addr):
        addr = addr.upper()
        print(f"_parse_addr {self._registers_list.get(addr, None)}")
        return self._registers_list.get(addr, None)

    def _get_register(self, addr):
        addr = addr.upper()
        if _register := self._registers_list.get(addr, None):
            return _register
        raise SyntaxError(msg="next link not found; check the instruction")

    def _write_next_PC(self, *args, **kwargs):
        return self.super_memory._write_and_update_pc(*args, **kwargs)

    def opcode_fetch(self, func, command, *args, **kwargs) -> None:
        print(f"opcode fetch -- {command}")
        command = command.replace(",", "")
        if _hex_in_com := re.search("0x[0-9a-fA-Z]+", command):
            command = command.replace(_hex_in_com.group(), "")
        command = command.strip()
        regex = re.compile(command.upper())
        _search_opcode = list(filter(regex.fullmatch, list(func.opcodes.keys())))
        print(_search_opcode)
        if _search_opcode:
            _hex_opcode = func.opcodes.get(_search_opcode[0])
            self._write_next_PC(_hex_opcode)
            return True
        raise OPCODENotFound

    def _write_opcode(self, data) -> bool:
        data_bytes = decompose_byte(data)
        for _byte in data_bytes[::-1]:
            print(f"{_byte=}")
            self._write_next_PC(_byte)
        return True

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.read(addr)
        data = self.memory.get(addr)
        # self._write_opcode(data)
        return data

    def memory_write(self, addr, data, log=True) -> bool:
        print(f"memory write {addr}|{data}")
        if _parsed_addr := self._parse_addr(addr):
            if log:
                self._write_opcode(data)
            return _parsed_addr.write(data, addr)
        if log:
            self._write_opcode(addr)
        self.memory[addr] = data
        return True

    def register_pair_read(self, addr) -> Byte:
        print(f"register pair read {addr}")
        _register = self._get_register(addr)
        data = _register.read_pair()
        # self._write_opcode(data)
        return data

    def register_pair_write(self, addr, data, log=True) -> bool:
        print(f"register pair write {addr}|{data}")
        if log:
            self._write_opcode(data)
        _register = self._get_register(addr)
        _register.write_pair(data)
        return True

    pass
