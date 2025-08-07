# MicroPython modules
import binascii
import struct


def addr_to_str(addr: bytes, reverse=False) -> str:
    if reverse:
        addr = bytes(addr[i] for i in range(len(addr) - 1, -1, -1))

    return binascii.hexlify(addr, ":").decode()


def addr_type_to_str(addr_type: int):
    if addr_type == 0:
        return "Public"

    elif addr_type == 1:
        return "Random Static"

    elif addr_type == 2:
        return "Resolvable Private"

    elif addr_type == 3:
        return "Non-Resolvable Private"

    else:
        return "".join(("Unknown (", str(addr_type), ")"))


def append_adv_packet(payload: bytearray, adv_type: int, value: bytes | bytearray):
    """Advertising payloads are repeated packets of the following form:
    1 byte data length (N + 1)
    1 byte type
    N bytes type-specific data"""

    payload.extend(struct.pack("BB", len(value) + 1, adv_type) + value)
