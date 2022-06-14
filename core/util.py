import re


def twos_complement(num: str, _base: int = 16) -> str:
    """
    Helper function to compure 2's complement of a hex value.

    Parameters
    ----------
    num : `str`
    _base : `int`, optional
        Defaults to 16
    """
    _bytes = int(len(format(int(num, _base), "x")) / 2) or 1
    return format((1 << 8 * _bytes) - int(num, _base), f"#0{2 + _bytes*2}x")


def comparehex(hex1: str, hex2: str) -> bool:
    """
    Helper function to compare two hex values.

    Parameters
    ----------
    hex1 : `str`
    hex2 : `str`
    """
    if int(str(hex1), 16) == int(str(hex2), 16):
        return True
    return False


def tohex(data: str) -> str:
    """
    Helper function to convert multiple patterns (`0x12`, `0X12`, `12H` and `12h`) into
    a single standard pattern.

    Parameters
    ----------
    data : `str`
    """
    match = re.fullmatch(r"^0[x|X][0-9a-fA-F]+", data)
    if match:
        return data.lower()
    match = re.fullmatch(r"^[0-9a-fA-F]+[h|H]$", data)
    if not match:
        raise ValueError(f"Required hex of the form `0x` or `H` found {data}")
    match = re.match(r"^[0-9a-fA-F]+", data)
    return f"0x{match.group().lower()}"


def ishex(data: str) -> bool:
    """
    Helper function to check if the value is hex or not.

    Parameters
    ----------
    data : `str`
    """
    return bool(re.fullmatch(r"^0[x|X][0-9a-fA-F]+", data)) or bool(re.fullmatch(r"^[0-9a-fA-F]+[h|H]$", data))


def sanatize_hex(data: str) -> str:
    """
    Helper function to sanatize hex value.

    Parameters
    ----------
    data : `str`
    """
    return data.replace("0x", "").replace("0X", "")


def decompose_byte(data: str, nibble: bool = False) -> list:
    """
    Helper function to decompose hex into bytes/nibbles

    Parameters
    ----------
    data : `str`
    nibble : `bool`, optional
        Defaults to `False`
    """
    _bytes = int(len(sanatize_hex(data)) / 2)
    mem_size = 8
    if nibble:
        mem_size = 4
    binary_data = format(int(str(data), 16), f"0{_bytes*8}b")
    return [
        format(int(binary_data[mem_size * x : mem_size * (x + 1)], 2), f"#0{int(mem_size/2)}x")
        for x in range(0, int(len(binary_data) / mem_size))
    ]


def get_bytes(data: str) -> int:
    """
    Helper function to get the # of bytes in the hex.

    Parameters
    ----------
    data : `str`
    """
    data = str(data)
    return int(len(sanatize_hex(data)) / 2)


def construct_hex(hex1: str, hex2: str, _bytes: int = 2) -> str:
    """
    Helper method to construct hex from two decomposed hex values.

    Parameters
    ----------
    hex1 : `str`
    hex2 : `str`
    _bytes : `int`, optional
        Defaults to 2
    """
    bin1 = format(int(str(hex1), 16), f"0{_bytes * 4}b")
    bin2 = format(int(str(hex2), 16), f"0{_bytes * 4}b")
    bin_total = "".join(["0b", bin1, bin2])
    return f'0x{format(int(bin_total, 2), f"0{_bytes * 2}x")}'
