from core.exceptions import OPCODENotFound, SyntaxError
from core.flags import flags
from core.memory import Byte, SuperMemory
from core.opcodes import opcodes_lookup
from core.util import decompose_byte, ishex, tohex


class Operations:
    def __init__(self) -> None:
        """
        Implements the I/O operations.
        """
        flags.reset()
        self.flags = flags
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
            "SP": self.super_memory.SP,
            "PC": self.super_memory.PC,
            "M": self.super_memory.M,
        }
        self._lookup_opcodes_dir = opcodes_lookup

        self._keywords = []
        self._generate_keywords()
        self._assembler = {}
        pass

    def _generate_keywords(self):
        """Generates a list of keywords to exclude."""
        _keywords = [*self._lookup_opcodes_dir.keys(), *self._registers_list.keys()]
        for key in _keywords:
            self._keywords.extend(key.split(" "))
        return

    def iskeyword(self, arg: str):
        """
        opcodes + registers. Checks if the `arg` is a keyword.

        Parameters
        ----------
        arg : `str`
        """
        if arg.upper() in self._keywords:
            return True
        return False

    def inspect(self):
        return "\n\n".join([flags.inspect(), self.super_memory.inspect()])

    def _parse_addr(self, addr: str):
        """
        Method to parse an address
        
        Parameters
        ----------
        addr : `str`
            Address
        """
        addr = addr.upper()
        return self._registers_list.get(addr, None)

    def _get_register(self, addr: str):
        """
        Returns the register from `addr`
        
        Parameters
        ----------
        addr : `str`
        """
        addr = addr.upper()
        _register = self._registers_list.get(addr, None)
        if _register:
            return _register
        raise SyntaxError(msg="next link not found; check the instruction")

    def _opcode_fetch(self, opcode: str, *args, **kwargs) -> None:
        """
        opcode fetch
        Fetches the hex code of an instruction from `opcode`

        Parameters
        ----------
        opcode : `str`
        """
        _args_params = [x for x in args if self.iskeyword(x)]
        _args_hexs = [decompose_byte(tohex(x)) for x in args if ishex(x)]
        _opcode_search_params = " ".join([opcode, *_args_params]).upper()
        _opcode_hex = self._lookup_opcodes_dir.get(_opcode_search_params)
        if _opcode_hex:
            return _opcode_hex, _args_hexs
        raise OPCODENotFound

    def prepare_operation(self, command: str, opcode: str, *args, **kwargs) -> bool:
        """
        Method to prepare the upcoming instruction, i.e. opcode fetch, assembler output etc.
        
        Parameters
        ----------
        command : `str`
        opcode : `str`
        """
        _opcode_hex, _args_hex = self._opcode_fetch(opcode, *args)
        self.super_memory.PC.write(_opcode_hex)
        _assembler = [_opcode_hex]
        for x in _args_hex:
            for y in x[::-1]:
                self.super_memory.PC.write(y)
                _assembler.append(y)
        self._assembler[command] = " ".join(_assembler).lower()
        return True

    def memory_read(self, addr: str) -> Byte:
        """
        Returns the contents of memory location pointed by `addr`.

        Parameters
        ----------
        addr : `str`
            Memory address location
        """
        print(f"memory read {addr}")
        _parsed_addr = self._parse_addr(addr)
        if _parsed_addr:
            return _parsed_addr.read(addr)
        data = self.memory.read(addr)
        return data

    def memory_write(self, addr: str, data) -> bool:
        """
        Writes the `data` at the memory location pointed by `addr`

        Parameters
        ----------
        addr : `str`
            Memory address
        data : `str`
            Hexadecimal data
        """
        addr = str(addr)
        print(f"memory write {addr}|{data}")
        _parsed_addr = self._parse_addr(addr)
        if _parsed_addr:
            return _parsed_addr.write(data, addr)
        self.memory.write(addr, data)
        return True

    def register_pair_read(self, addr) -> Byte:
        """
        Method to read and return the data of the register pair pointed by `addr`
        
        Parameters
        ----------
        addr : `str`
        """
        print(f"register pair read {addr}")
        _register = self._get_register(addr)
        data = _register.read_pair()
        # self._write_opcode(data)
        return data

    def register_pair_write(self, addr, data) -> bool:
        """
        Method to write the data of the register pair pointed by `addr`
        
        Parameters
        ----------
        addr : `str`
        data : `str`
        """
        print(f"register pair write {addr}|{data}")
        _register = self._get_register(addr)
        _register.write_pair(data)
        return True

    pass
