def decompose_byte(data, _bytes=2, mem_size=8):
    len_bin = _bytes * mem_size
    binary_data = format(int(str(data), 16), "b")
    if len(binary_data) != len_bin:
        pad_required = len_bin - len(binary_data)
        binary_data = "0" * pad_required + binary_data
    return [hex(int(binary_data[mem_size * x : mem_size * (x + 1)], 2)) for x in range(0, _bytes)]


def construct_byte(data):
    pass
