# MicroPython modules
import bluetooth
import micropython

# Custom modules
import common.logger
import common.utils


IO_DISPLAY_ONLY = micropython.const(0)
IO_DISPLAY_YESNO = micropython.const(1)
IO_KEYBOARD_ONLY = micropython.const(2)
IO_NO_INPUT_OUTPUT = micropython.const(3)
IO_KEYBOARD_DISPLAY = micropython.const(4)


# 因 BLE.irq() 只能指定一個函數來處理 BLE 訊息，
# 所以需自行儲存要接收 BLE 訊息的函數
_irq_handlers = []


def _build_props(
    *,
    read=False,
    read_enc=False,
    read_authen=False,
    read_author=False,
    write=False,
    write_enc=False,
    write_authen=False,
    write_author=False,
    write_no_rsp=False,
    notify=False,
    indicate=False,
) -> int:
    flags = 0

    if read:
        flags |= 0x0002

    if read_enc:
        flags |= 0x0200

    if read_authen:
        flags |= 0x0400

    if read_author:
        flags |= 0x0800

    if write:
        flags |= 0x0008

    if write_enc:
        flags |= 0x1000

    if write_authen:
        flags |= 0x2000

    if write_author:
        flags |= 0x4000

    if write_no_rsp:
        flags |= 0x0004

    if notify:
        flags |= 0x0010

    if indicate:
        flags |= 0x0020

    return flags


class Characteristic:
    """GATT Characteristic"""

    def __init__(
        self,
        uuid: int | str,
        *,
        read=False,
        read_enc=False,
        read_authen=False,
        read_author=False,
        write=False,
        write_enc=False,
        write_authen=False,
        write_author=False,
        write_no_rsp=False,
        notify=False,
        indicate=False,
    ):
        self.uuid = bluetooth.UUID(uuid)
        self.char_flags = _build_props(
            read=read,
            read_enc=read_enc,
            read_authen=read_authen,
            read_author=read_author,
            write=write,
            write_enc=write_enc,
            write_authen=write_authen,
            write_author=write_author,
            write_no_rsp=write_no_rsp,
            notify=notify,
            indicate=indicate,
        )
        self.value_handle = 0

    def _to_tuple(self) -> tuple[bluetooth.UUID, int]:
        return (self.uuid, self.char_flags)


class Service:
    """GATT Service"""

    def __init__(self, uuid: int | str):
        self.uuid = bluetooth.UUID(uuid)
        self.chars: list[Characteristic] = []

    def add_char(self, char: Characteristic):
        self.chars.append(char)

    def _to_tuple(
        self,
    ) -> tuple[bluetooth.UUID, tuple[tuple[bluetooth.UUID, int], ...]]:
        return (self.uuid, tuple(c._to_tuple() for c in self.chars))


class Server:
    """GATT Server"""

    def _build_services(self) -> tuple[Service, ...]:
        """由子類別負責建立所需的 Service 物件"""
        return tuple()

    def register_services(self):
        # 儲存所有的 Service 物件
        self.srvs = self._build_services()

        handles = _register_services(tuple(s._to_tuple() for s in self.srvs))

        for i, s in enumerate(self.srvs):
            char_handles = handles[i]

            for j, char in enumerate(s.chars):
                h = char_handles[j]
                char.value_handle = h


def init():
    ble = bluetooth.BLE()
    ble.irq(_ble_isr)
    ble.active(True)


def get_mac():
    ble = bluetooth.BLE()
    return ble.config("mac")


def _register_services(services_definition: tuple):
    ble = bluetooth.BLE()
    return ble.gatts_register_services(services_definition)


def advertise(
    interval_us: int, adv_data=None, *, resp_data=None, connectable: bool = True
):
    ble = bluetooth.BLE()
    ble.gap_advertise(
        interval_us, adv_data, resp_data=resp_data, connectable=connectable
    )


def set_pairing_mode(*, bond: bool, mitm: bool, le_secure: bool):
    ble = bluetooth.BLE()
    ble.config(bond=bond)
    ble.config(mitm=mitm)
    ble.config(le_secure=le_secure)


def set_io(io):
    ble = bluetooth.BLE()
    ble.config(io=io)


def set_passkey(conn_handle: int, action: int, passkey: int | str):
    ble = bluetooth.BLE()
    ble.gap_passkey(conn_handle, action, int(passkey))


def gatts_read(value_handle: int):
    ble = bluetooth.BLE()
    return ble.gatts_read(value_handle)


def gatts_write(value_handle: int, data: bytes, send_update: bool = False):
    ble = bluetooth.BLE()
    ble.gatts_write(value_handle, data, send_update)


def notify(conn_handle: int, value_handle: int, data: bytes | None = None):
    common.logger.write(
        "".join(
            (
                "Notify(value_handle: ",
                str(value_handle),
                ", data: ",
                common.utils.array_to_hex_str(data),
                ")",
            )
        )
    )
    ble = bluetooth.BLE()
    ble.gatts_notify(conn_handle, value_handle, data)


def indicate(conn_handle: int, value_handle: int, data: bytes | None = None):
    common.logger.write(
        "".join(
            (
                "Indicate(value_handle: ",
                str(value_handle),
                ", data: ",
                common.utils.array_to_hex_str(data),
                ")",
            )
        )
    )
    ble = bluetooth.BLE()
    ble.gatts_indicate(conn_handle, value_handle, data)


def register_irq_handler(handler):
    _irq_handlers.append(handler)


def _ble_isr(event, data):
    ret = None

    # 處理訊息後，分發 BLE IRQ 給所有訂閱的函式
    for h in _irq_handlers:
        r = h(event, data)

        if r is not None:
            ret = r

    return ret
