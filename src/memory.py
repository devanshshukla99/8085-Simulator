import re
import textwrap
from src.exceptions import ValueErrorHexRequired, InvalidMemoryAddress, MemoryLimitExceeded


class Byte:
    def __init__(self, data=None, _bytes=1, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._bytes = _bytes
        self._mem_limit = "".join(["0x", "FF" * _bytes])
        self.data = "".join(["0x", "00" * _bytes])
        if data:
            self.data = data
        return

    def __str__(self) -> str:
        return f"{self._data}"

    def __repr__(self) -> str:
        return f"{self._data}"

    def __int__(self) -> str:
        return int(self._data, 16)

    def __call__(self, value):
        self.data = value

    def __next__(self):
        self.data = format(int(str(self.data), 16) + 1, f"#0{2 + self._bytes*2}x")
        return True

    def _next_addr(self):
        data = format(int(str(self.data), 16) + 1, "#06x")
        self.write(data)
        return True

    def replace(self, *args, **kwargs) -> None:
        return self._data.replace(*args, **kwargs)

    def lower(self):
        return self._data.lower()

    def upper(self):
        return self._data.upper()

    def read(self, *args):
        return self.data

    def write(self, data, *args):
        self.data = data
        return True

    def _verify_hex(self, value):
        if type(value) is Byte:
            return True
        if not re.fullmatch("^0[x|X][0-9a-fA-F]+", value):
            raise ValueErrorHexRequired(value)
        return True

    def _verify_limit(self, value):
        if int(str(value), 16) > int(self._mem_limit, 16):
            raise MemoryLimitExceeded
        return True

    def _verify(self, value):
        if self._verify_hex(value):
            if self._verify_limit(value):
                return True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if self._verify(value):
            self._data = str(value).lower()

    pass


class Memory(dict):
    def __init__(self, memory_size=65535, starting_address="0x0000", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._starting_address = starting_address
        self._memory_size = memory_size
        self._memory_limit = hex(int(starting_address, 16) + memory_size)
        self._default_mem = Byte("0x00")

    def _verify_sanatize(self, value):
        if not re.fullmatch("^0[x|X][0-9a-fA-F]+", str(value)):
            raise InvalidMemoryAddress()
        if int(str(value), 16) > int(self._memory_limit, 16):
            raise MemoryLimitExceeded()
        return format(int(str(value), 16), "#06x")

    def __getitem__(self, addr):
        addr = self._verify_sanatize(addr)
        if addr not in self:
            self.__setitem__(addr, self._default_mem)
            return self._default_mem
        return super().__getitem__(addr)

    def __setitem__(self, addr, value) -> None:
        addr = self._verify_sanatize(addr)
        return super().__setitem__(addr, Byte(value))

    def sort(self):
        return dict(sorted(self.items(), key=lambda x: int(str(x[0]), 16)))

    def read(self, *args, **kwargs):
        return self.__getitem__(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.__setitem__(*args, **kwargs)

    pass


class RegisterPair:
    def __init__(self, reg_1, reg_2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reg_1 = reg_1
        self._reg_2 = reg_2
        self._registers = {
            reg_1: Byte(),
            reg_2: Byte(),
        }
        self._bytes = 2
        self.keys = self._registers.keys
        self.values = self._registers.values
        self.items = self._registers.items
        return

    def __getitem__(self, key):
        return self._registers.get(key).read()

    def __setitem__(self, key, value):
        return self._registers.get(key).write(value)

    def __repr__(self):
        return f"{self._registers.get(self._reg_1)} {self._registers.get(self._reg_2)}"

    def read(self, addr) -> Byte:
        return self._registers.get(str(addr).upper())

    def read_pair(self) -> str:
        bin1 = format(int(str(self._registers.get(self._reg_1).read()), 16), f"0{self._bytes * 4}b")
        bin2 = format(int(str(self._registers.get(self._reg_2).read()), 16), f"0{self._bytes * 4}b")
        bin_total = "".join(["0b", bin1, bin2])
        return f'0x{format(int(bin_total, 2), f"0{self._bytes * 2}x")}'

    def write(self, data, addr) -> bool:
        return self._registers.get(str(addr).upper()).__call__(data)

    def write_pair(self, data) -> bool:
        mem_size = 8
        binary_data = format(int(str(data), 16), f"0{self._bytes*8}b")
        data_1, data_2 = [
            format(int(binary_data[mem_size * x : mem_size * (x + 1)], 2), f"#0{int(mem_size/2)}x")
            for x in range(0, int(len(binary_data) / mem_size))
        ]
        self._registers.get(str(self._reg_1).upper()).__call__(data_1)
        self._registers.get(str(self._reg_2).upper()).__call__(data_2)
        return True


class Registers:
    def __init__(self) -> None:
        self.A = Byte()
        self.PSW = Byte()
        self.BC = RegisterPair("B", "C")
        self.DE = RegisterPair("D", "E")
        self.HL = RegisterPair("H", "L")
        self.SP = RegisterPair("S", "P")
        self.PC = Byte(_bytes=2)
        setattr(self.M.__func__, "read", lambda *args: self.HL.read_pair())
        return

    def M(self):
        return

    def inspect(self):
        return textwrap.dedent(
            f"""
            Registers
            ---------
            A/PSW = {self.A} {self.PSW}
            BC = {self.BC}
            DE = {self.DE}
            HL = {self.HL}
            SP = {self.SP}
            PC = {self.PC}
            """
        )
    pass


class SuperMemory:
    def __init__(self) -> None:
        self.memory = Memory(65535, "0x0000")

        self.A = Byte()
        self.PSW = Byte()
        self.BC = RegisterPair("B", "C")
        self.DE = RegisterPair("D", "E")
        self.HL = RegisterPair("H", "L")
        self.SP = RegisterPair("S", "P")
        self.PC = Byte(_bytes=2)
        setattr(self.M.__func__, "read", lambda *args: self.memory[self.HL.read_pair()])
        setattr(self.M.__func__, "write", lambda data, *args: self.memory.write(self.HL.read_pair(), data))
        pass

    def M(self):
        return

    def _reg_inspect(self):
        return textwrap.dedent(
            f"""
            Registers
            ---------
            A/PSW = {self.A} {self.PSW}
            BC = {self.BC}
            DE = {self.DE}
            HL = {self.HL}
            SP = {self.SP}
            PC = {self.PC}
            """
        )

    def inspect(self):
        return "\n\n".join([self._reg_inspect(), str(self.memory.sort())])

    def _write_and_update_pc(self, data):
        self.memory[str(self.PC)] = data
        next(self.PC)
        return True
