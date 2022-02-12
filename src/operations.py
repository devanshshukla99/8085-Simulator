import re
import json
from src.memory import Byte, SuperMemory
from src.flags import flags
from src.exceptions import OPCODENotFound, SyntaxError
from src.util import decompose_byte, ishex


class Operations:
    def __init__(self) -> None:
        flags.reset()
        self.flags = flags
        self.super_memory = SuperMemory()
        self.memory = self.super_memory.memory
        self._update_pc = self.super_memory._update_pc
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
        with open("src/opcodes.json", "r") as f:
            self._lookup_opcodes_dir = json.load(f)

        self._keywords = []
        self._generate_keywords()
        pass

    def _generate_keywords(self):
        _keywords = [*self._lookup_opcodes_dir.keys(), *self._registers_list.keys()]
        for key in _keywords:
            self._keywords.extend(key.split(" "))
        return

    def iskeyword(self, arg):
        """
        opcodes + registers
        """
        if arg.upper() in self._keywords:
            return True
        return False

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

    def _opcode_fetch(self, opcode, *args, **kwargs) -> None:
        _args_params = [x for x in args if self.iskeyword(x)]
        print(f"##{_args_params}##")
        _args_hexs = [decompose_byte(x) for x in args if ishex(x)]
        print(f"##{_args_hexs}##")
        _opcode_search_params = " ".join([opcode, *_args_params]).upper()
        print(f"**{_opcode_search_params}**")
        if _opcode_hex := self._lookup_opcodes_dir.get(_opcode_search_params):
            return _opcode_hex, _args_hexs
        raise OPCODENotFound

    def prepare_operation(self, opcode, *args, **kwargs) -> bool:
        _opcode_hex, _args_hex = self._opcode_fetch(opcode, *args)
        self._update_pc(_opcode_hex)
        for x in _args_hex:
            for y in x[::-1]:
                self._update_pc(y)
        return True

    def memory_read(self, addr) -> Byte:
        print(f"memory read {addr}")
        if _parsed_addr := self._parse_addr(addr):
            return _parsed_addr.read(addr)
        data = self.memory.read(addr)
        # self._write_opcode(data)
        return data

    def memory_write(self, addr, data, log=True) -> bool:
        print(f"memory write {addr}|{data}")
        if _parsed_addr := self._parse_addr(addr):
            # if log:
            #     self._write_opcode(data)
            return _parsed_addr.write(data, addr)
        # if log:
        #     self._write_opcode(addr)
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
        # if log:
        #     self._write_opcode(data)
        _register = self._get_register(addr)
        _register.write_pair(data)
        return True

    pass
