def write_uint16(result: bytearray | memoryview, index: int, value: int):
    result[index] = value & 0xFF
    result[index + 1] = (value >> 8) & 0xFF


def write_uint24(result: bytearray | memoryview, index: int, value: int):
    result[index] = value & 0xFF
    result[index + 1] = (value >> 8) & 0xFF
    result[index + 2] = (value >> 16) & 0xFF


def array_to_hex_str(
    array: list[int] | tuple[int, ...] | bytes | memoryview | None,
    is_array_format: bool = True,
) -> str:
    """Convert an array of integers to a hex string.
    Example:
        array = [0x12, 0x34]

        If is_array_format is True, the result is "[0x12, 0x34]".
        Otherwise, the result is "0x3412".
    """

    if array is None:
        return str(None)

    elif len(array) == 0:
        return ""

    elif is_array_format:
        return "[" + ", ".join(f"0x{n:02X}" for n in array) + "]"

    else:
        return "0x" + "".join(f"{array[i]:02X}" for i in range(len(array) - 1, -1, -1))
