# Custom modules
import ble.e2e
import ble.mixin
import ble.stack
import common.sfloat
import common.utils
import config


class IddFeatures(ble.mixin.ReadMixin, ble.stack.Characteristic):
    def __init__(self, config: config.Config):
        ble.stack.Characteristic.__init__(self, 0x2B23, read=True)

        self._config = config

    def _build_read_rsp(self, buf: memoryview) -> int:
        buf[0] = 0xFF  # Low byte of E2E-CRC
        buf[1] = 0xFF  # High byte of E2E-CRC
        buf[2] = 0x00  # E2E-Counter

        t = common.sfloat.float_to_sfloat(self._config.idd_features_insulin_conc)
        common.utils.write_uint16(buf, 3, t)

        common.utils.write_uint24(buf, 5, self._config.idd_features_flags)

        return 8


class E2EIddFeatures(ble.mixin.E2ETxMixin, IddFeatures):
    def __init__(self, config: config.Config):
        ble.mixin.E2ETxMixin.__init__(self)
        IddFeatures.__init__(self, config)

    def _build_read_rsp(self, buf: memoryview) -> int:
        data_len = super()._build_read_rsp(buf)
        buf[2] = self._tx_counter.value
        ble.e2e.Crc.fill_crc(buf, 0, data_len)
        return data_len
