import re
import textwrap
from src.exceptions import ValueErrorHexRequired, InvalidMemoryAddress, MemoryLimitExceeded


class AncientMemory(dict):
    def __init__(self, starting_address=0x0000, memory_size=4096) -> None:
        raise NotImplementedError
        super().__init__()
        for idx in range(memory_size):
            self[int(starting_address) + idx] = "0x0000"

    def __setitem__(self, __k, value) -> None:
        _match = re.fullmatch("^0x[0-9a-fA-F]+", value)
        if not _match:
            raise ValueErrorHexRequired
        if int(value, 16) > int("0xFFFF", 16):
            raise MemoryLimitExceeded
        return super().__setitem__(__k, value)

    pass


class Byte:
    def __init__(self, data=None, _bytes=1) -> None:
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

    def read(self):
        return self.data

    def write(self, data):
        self.data = data
        return True

    def _verify_hex(self, value):
        if type(value) is Byte:
            return True
        if not re.fullmatch("^0x[0-9a-fA-F]+", value):
            raise ValueErrorHexRequired()
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
            self._data = value

    pass


class OldMemory(dict):
    """
    0x00 = 0000 0000 (1 byte)
    """

    def __init__(self, memory_size=4096, starting_address="0x0000", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._starting_address = starting_address
        self._memory_size = memory_size
        self._memory_limit = hex(int(starting_address, 16) + memory_size)
        self._default_mem = "0x00"

    def _verify_hex(self, value):
        if not re.fullmatch("^0x[0-9a-fA-F]+", value):
            raise ValueErrorHexRequired()
        return True

    def _verify_address(self, value):
        if not self._verify_hex(value):
            return False
        if int(value, 16) > int(self._memory_limit, 16):
            raise MemoryLimitExceeded()
        return True

    def __getitem__(self, __k):
        if __k not in self:
            if not self._verify_address(__k):
                raise InvalidMemoryAddress()
            return self._default_mem
        return super().__getitem__(__k)

    def __setitem__(self, __k, value) -> None:
        if self._verify_hex(value):
            if int(value, 16) > int("0xFF", 16):
                raise MemoryLimitExceeded()
            return super().__setitem__(__k, value)

    pass


class Memory(dict):
    def __init__(self, memory_size=4096, starting_address="0x0000", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._starting_address = starting_address
        self._memory_size = memory_size
        self._memory_limit = hex(int(starting_address, 16) + memory_size)
        self._default_mem = Byte("0x00")

    def _verify_hex(self, value):
        if type(value) is Byte:
            return True
        if not re.fullmatch("^0x[0-9a-fA-F]+", value):
            raise ValueErrorHexRequired()
        return True

    def _verify_address(self, value):
        if not self._verify_hex(value):
            return False
        if int(str(value), 16) > int(self._memory_limit, 16):
            raise MemoryLimitExceeded()
        return True

    def get(self, __k):
        return self.__getitem__(__k)

    def __getitem__(self, __k):
        if __k not in self:
            if not self._verify_address(__k):
                raise InvalidMemoryAddress()
            self.__setitem__(__k, self._default_mem)
            return self._default_mem
        return super().__getitem__(__k)

    def __setitem__(self, __k, value) -> None:
        return super().__setitem__(__k, Byte(value))

    pass


class Registers:
    A = Byte()
    PSW = Byte()
    B = Byte()
    C = Byte()
    D = Byte()
    E = Byte()
    H = Byte()
    L = Byte()
    S = Byte()
    P = Byte()
    PC = Byte(_bytes=2)

    def inspect(self):
        return textwrap.dedent(
            f"""
            Registers
            ---------
            A/PSW = {self.A} {self.PSW}
            BC = {self.B} {self.C}
            DE = {self.D} {self.E}
            HL = {self.H} {self.L}
            SP = {self.S} {self.P}
            PC = {self.PC}
            """
        )
