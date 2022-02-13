import re
import textwrap

from core.exceptions import InvalidMemoryAddress, MemoryLimitExceeded


class Hex:
    def __init__(self, data: str = "0x00", _bytes: str = 1, *args, **kwargs) -> None:
        self._bytes = _bytes
        self._base = 16
        self._format_spec = f"#0{2 + _bytes * 2}x"
        self._format_spec_bin = f"#0{2 + _bytes * 4}b"
        self._memory_limit_hex = "FF" * _bytes
        self._memory_limit = int(self._memory_limit_hex, self._base)
        self.data = data
        return

    def __call__(self, value: str):
        self.data = value

    def __str__(self) -> str:
        return self._data

    def __repr__(self) -> str:
        return self._data

    def __call__(self, val) -> None:
        self.data = val

    def __int__(self) -> int:
        return int(self._data, self._base)

    def __index__(self) -> int:
        return int(self._data, self._base)

    def __format__(self, format_spec: str = None) -> str:
        if not format_spec:
            format_spec = self._format_spec
        return format(int(self._data, self._base), format_spec)

    def __next__(self):
        self._data = format(int(self._data, self._base) + 1, self._format_spec)
        return self._data

    def __add__(self, val: int):
        return Hex(format(int(self._data, self._base) + val, self._format_spec), _bytes=self._bytes)

    def __sub__(self, val: int):
        return Hex(format(int(self._data, self._base) - val, self._format_spec), _bytes=self._bytes)

    def __len__(self):
        return self._bytes

    def _verify(self, value: str):
        if not re.fullmatch("^0[x|X][0-9a-fA-F]+", str(value)):
            raise InvalidMemoryAddress()
        if int(str(value), self._base) > self._memory_limit:
            raise MemoryLimitExceeded()

    def bin(self) -> str:
        return format(int(self._data, self._base), self._format_spec_bin)

    @property
    def data(self) -> str:
        return self._data

    @data.setter
    def data(self, val: str) -> None:
        self._verify(val)
        self._data = format(int(str(val), self._base), self._format_spec)
        return

    def read(self, *args, **kwargs) -> str:
        return self

    def write(self, val: str, *args, **kwargs) -> bool:
        self.data = val
        return True

    def update(self, val: str, *args, **kwargs) -> bool:
        return self.write(val, *args, **kwargs)

    def replace(self, *args, **kwargs) -> None:
        return self._data.replace(*args, **kwargs)

    def lower(self, *args, **kwargs):
        return self._data.lower(*args, **kwargs)

    def upper(self, *args, **kwargs):
        return self._data.upper(*args, **kwargs)

    pass


class Byte(Hex):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    pass


class Memory(dict):
    def __init__(self, memory_size=65535, starting_address="0x0000", _bytes=2, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._bytes = 1
        self._base = 16
        self._memory_size = memory_size
        self._starting_address = starting_address

        self._default_mem = "0x00"
        self._format_spec = f"#0{2 + _bytes * 2}x"
        self._format_spec_bin = f"#0{2 + _bytes * 4}b"
        self._memory_limit = int(starting_address, 16) + memory_size
        self._memory_limit_hex = format(self._memory_limit, self._format_spec)
        return

    def __getitem__(self, addr: str) -> str:
        addr = self._verify(addr)
        if addr not in self:
            super().__setitem__(addr, Byte(self._default_mem))
        return super().__getitem__(addr)

    def __setitem__(self, addr: str, value: str) -> None:
        addr = self._verify(addr)
        if addr not in self:
            super().__setitem__(addr, Byte(value))
        return super().__getitem__(addr).write(value)

    def _verify(self, value: str) -> None:
        if not re.fullmatch("^0[x|X][0-9a-fA-F]+", str(value)):
            raise InvalidMemoryAddress()
        if int(str(value), self._base) > self._memory_limit:
            raise MemoryLimitExceeded()
        return format(int(value, self._base), self._format_spec)

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
        self._base = 16
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
        bin1 = format(int(str(self._registers.get(self._reg_1).read()), self._base), f"0{self._bytes * 4}b")
        bin2 = format(int(str(self._registers.get(self._reg_2).read()), self._base), f"0{self._bytes * 4}b")
        bin_total = "".join(["0b", bin1, bin2])
        return f'0x{format(int(bin_total, 2), f"0{self._bytes * 2}x")}'

    def write(self, data, addr) -> bool:
        return self._registers.get(str(addr).upper()).__call__(data)

    def write_pair(self, data) -> bool:
        mem_size = 8
        binary_data = format(int(str(data), self._base), f"0{self._bytes*8}b")
        data_1, data_2 = [
            format(int(binary_data[mem_size * x : mem_size * (x + 1)], 2), f"#0{int(mem_size/2)}x")
            for x in range(0, int(len(binary_data) / mem_size))
        ]
        self._registers.get(str(self._reg_1).upper()).__call__(data_1)
        self._registers.get(str(self._reg_2).upper()).__call__(data_2)
        return True


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

    def _registers_todict(self):
        return {
            "A/PSW": f"{self.A} {self.PSW}",
            "BC": f"{self.BC}",
            "DE": f"{self.DE}",
            "HL": f"{self.HL}",
            "SP": f"{self.SP}",
            "PC": f"{self.PC}",
        }

    def _update_pc(self, data):
        self.memory[str(self.PC)] = data
        next(self.PC)
        return True

    def inspect(self):
        return "\n\n".join([self._reg_inspect(), str(self.memory.sort())])

    pass
