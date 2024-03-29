import re

from core.exceptions import InvalidMemoryAddress, MemoryLimitExceeded


class Hex:
    def __init__(self, data: str = "0x00", _bytes: int = 1, *args, **kwargs) -> None:
        """
        Implements the idea of a Hexadecimal with additional methods.

        Parameters
        ----------
        data : `str`, optional
            Defaults to `0x00`
        _bytes : `int`, optional
            Defaults to `1`
        """
        self._bytes = _bytes
        self._base = 16
        self._format_spec = f"#0{2 + _bytes * 2}x"
        self._format_spec_bin = f"#0{2 + _bytes * 8}b"
        self._memory_limit_hex = "FF" * _bytes
        self._memory_limit = int(self._memory_limit_hex, self._base)
        self.data = data
        return

    def __call__(self, value: str) -> None:
        self.data = value

    def __str__(self) -> str:
        return self._data

    def __repr__(self) -> str:
        return self._data

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
        """
        Verifies if the `hex` val is in correct format.

        Parameters
        ----------
        value : `str`
        """
        if not re.fullmatch("^0[x|X][0-9a-fA-F]+", str(value)):
            raise InvalidMemoryAddress()
        if int(str(value), self._base) > self._memory_limit:
            raise MemoryLimitExceeded()

    def bin(self) -> str:
        """Returns the binary value of the instantiated hex"""
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
        """Returns the hex value"""
        return self

    def write(self, val: str, *args, **kwargs) -> bool:
        """
        Updates the current hex-data

        Parameters
        ----------
        val : `str`
            Hex data
        """
        self.data = val
        return True

    def update(self, val: str, *args, **kwargs) -> bool:
        """Wrapper for `Hex.write`"""
        return self.write(val, *args, **kwargs)

    def replace(self, *args, **kwargs) -> None:
        """Wrapper for `str.replace`"""
        return self._data.replace(*args, **kwargs)

    def lower(self, *args, **kwargs):
        """Wrapper for `str.lower`"""
        return self._data.lower(*args, **kwargs)

    def upper(self, *args, **kwargs):
        """Wrapper for `str.upper`"""
        return self._data.upper(*args, **kwargs)

    pass


class Byte(Hex):
    def __init__(self, *args, **kwargs) -> None:
        """
        Child class for byte instantiation.
        """
        super().__init__(*args, **kwargs)

    pass
