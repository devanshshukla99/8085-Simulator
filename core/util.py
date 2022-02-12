import re


def twos_complement(num, _base=16):
    _bytes = int(len(format(int(num, _base), "x")) / 2) or 1
    return format((1 << 8 * _bytes) - int(num, _base), f"#0{2 + _bytes*2}x")


def comparehex(hex1, hex2):
    if int(str(hex1), 16) == int(str(hex2), 16):
        return True
    return False


def ishex(data):
    return bool(re.fullmatch(r"^0[x|X][0-9a-fA-F]+", data))


def sanatize_hex(data):
    return data.replace("0x", "").replace("0X", "")


def decompose_byte(data, nibble=False):
    _bytes = int(len(sanatize_hex(data)) / 2)
    mem_size = 8
    if nibble:
        mem_size = 4
    binary_data = format(int(str(data), 16), f"0{_bytes*8}b")
    return [
        format(int(binary_data[mem_size * x : mem_size * (x + 1)], 2), f"#0{int(mem_size/2)}x")
        for x in range(0, int(len(binary_data) / mem_size))
    ]


def get_bytes(data):
    data = str(data)
    return int(len(sanatize_hex(data)) / 2)


def construct_hex(hex1, hex2, _bytes=2):
    bin1 = format(int(str(hex1), 16), f"0{_bytes * 4}b")
    bin2 = format(int(str(hex2), 16), f"0{_bytes * 4}b")
    print(bin1)
    print(bin2)
    bin_total = "".join(["0b", bin1, bin2])
    return f'0x{format(int(bin_total, 2), f"0{_bytes * 2}x")}'
