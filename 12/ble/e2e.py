class Counter:
    def __init__(self, init_value):
        self.value = self._init_value = init_value

    def reset(self):
        self.value = self._init_value

    def inc_counter(self):
        counter = self.value + 1
        self.value = (counter >> 8) + (counter & 0xFF)


class TxCounter(Counter):
    def __init__(self):
        super().__init__(1)


class RxCounter(Counter):
    def __init__(self):
        super().__init__(255)

    def check(self, received_counter: int) -> bool:
        return received_counter - (self.value % 255) == 1


class Crc:
    """CRC16-CCITT from LSB."""

    @classmethod
    def fill_crc(
        cls, data: list[int] | bytearray | memoryview, crc_position: int, data_len: int
    ):
        crc = cls()

        # if crc_position < 0:
        #     crc_position += data_len

        for i in range(0, crc_position):
            crc.add_int8(data[i])

        for i in range(crc_position + 2, data_len):
            crc.add_int8(data[i])

        data[crc_position] = crc.value & 0xFF
        data[crc_position + 1] = (crc.value >> 8) & 0xFF

    def __init__(self):
        self.value = 0xFFFF

    def add_int8(self, data: int):
        for bit in range(8):
            # 目前要處理的位元
            in_bit = (data >> bit) & 1

            msb = self.value & 1
            self.value >>= 1
            if in_bit ^ msb:
                # 0x8408 是將 0x1021 顛倒後的值
                self.value ^= 0x8408

    def add_bytes(self, data: list[int] | tuple[int] | bytes | bytearray):
        for n in data:
            self.add_int8(n)
