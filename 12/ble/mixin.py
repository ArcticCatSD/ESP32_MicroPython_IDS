# MicroPython modules
import micropython

# Custom modules
import ble.e2e
import ble.stack


_IRQ_CENTRAL_DISCONNECT = micropython.const(2)


_rbuf = bytearray(20)
_rbuf_mv = memoryview(_rbuf)


class E2ETxMixin:
    def __init__(self):
        self._tx_counter = ble.e2e.TxCounter()
        ble.stack.register_irq_handler(self._isr_e2e_tx_mixin)

    def _after_build_tx_data(self):
        self._tx_counter.inc_counter()

    def _isr_e2e_tx_mixin(self, event, data):
        if event == _IRQ_CENTRAL_DISCONNECT:
            self._tx_counter.reset()


class ReadMixin:
    def on_read(self, value_handle: int):
        n = self._build_read_rsp(_rbuf_mv)
        self._after_build_tx_data()

        # 將回覆資料寫入 characteristic 裡
        ble.stack.gatts_write(value_handle, _rbuf_mv[:n])

    def _build_read_rsp(self, buf: memoryview) -> int:
        """返回資料長度"""
        raise NotImplementedError

    def _after_build_tx_data(self):
        pass
