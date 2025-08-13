# MicroPython modules
import asyncio
import gc
import micropython
import struct

# Custom modules
import ble.ids.features
import ble.stack
import ble.utils
import common.logger
import config


# BLE 事件
_IRQ_CENTRAL_CONNECT = micropython.const(1)
_IRQ_CENTRAL_DISCONNECT = micropython.const(2)
_IRQ_GATTS_READ_REQUEST = micropython.const(4)
_IRQ_PASSKEY_ACTION = micropython.const(31)

# 配對類型
_PASSKEY_ACTION_DISPLAY = micropython.const(3)

# Insulin Delivery Service 相關 UUID
_IDS_UUID = micropython.const(0x183A)


_config = config.get_config()


class IdsServer(ble.stack.Server):
    def __init__(self):
        ble.stack.init()
        ble.stack.register_irq_handler(self._ble_isr)

        # 取得本地端的藍芽位址及類型
        mac = ble.stack.get_mac()
        common.logger.write(
            f"Local: {ble.utils.addr_to_str(mac[1])} ({ble.utils.addr_type_to_str(mac[0])})"
        )

        # 啟用安全機制
        ble.stack.set_pairing_mode(bond=True, mitm=True, le_secure=True)

        # 指定本裝置只能顯示連線密碼
        ble.stack.set_io(ble.stack.IO_DISPLAY_ONLY)

        self.rc_addr = None

    def _build_services(self) -> tuple[ble.stack.Service, ...]:
        return (self._build_ids(),)

    def _build_ids(self) -> ble.stack.Service:

        self._ids = ble.stack.Service(_IDS_UUID)

        if _config.is_e2e_protection_supported:
            features = ble.ids.features.E2EIddFeatures(_config)
        else:
            features = ble.ids.features.IddFeatures(_config)

        self._ids.add_char(features)

        return self._ids

    async def run(self):
        # 發送廣播
        adv_data = self._build_advertising_payload()
        resp_data = self._build_scan_response_payload(_config.local_name)
        ble.stack.advertise(_config.adv_interval_us, adv_data, resp_data=resp_data)

        # 主執行緒會一直等下去
        flag = asyncio.ThreadSafeFlag()

        gc.collect()
        print(f"Heap RAM: {gc.mem_free()} bytes\n")
        micropython.mem_info()

        await flag.wait()

    def _build_advertising_payload(self) -> bytes:
        # 廣播內容型態
        ADV_TYPE_FLAGS = 0x01
        ADV_TYPE_UUID16_COMPLETE = 0x3
        ADV_TYPE_APPEARANCE = 0x19

        # LE General Discoverable Mode
        LE_GENERAL_DISC_MODE = 0x02

        BR_EDR_NOT_SUPPORTED = 0x04

        GENERIC_INSULIN_PUMP = 0x0D40

        payload = bytearray()

        ble.utils.append_adv_packet(
            payload,
            ADV_TYPE_FLAGS,
            struct.pack("B", LE_GENERAL_DISC_MODE | BR_EDR_NOT_SUPPORTED),
        )
        ble.utils.append_adv_packet(
            payload, ADV_TYPE_UUID16_COMPLETE, struct.pack("<H", _IDS_UUID)
        )
        ble.utils.append_adv_packet(
            payload, ADV_TYPE_APPEARANCE, struct.pack("<H", GENERIC_INSULIN_PUMP)
        )

        return payload

    def _build_scan_response_payload(self, local_name: str) -> bytes:
        ADV_TYPE_COMPLETE_LOCAL_NAME = 0x09

        payload = bytearray()

        ble.utils.append_adv_packet(
            payload, ADV_TYPE_COMPLETE_LOCAL_NAME, local_name.encode("utf-8")
        )

        return payload

    def _ble_isr(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data

            self.rc_addr = bytes(addr)
            micropython.schedule(_log_connect, addr_type)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data

            self.rc_addr = bytes(addr)
            micropython.schedule(_log_disconnect, addr_type)

            # 要求 MicroPython 在 BLE 中斷後，儘快重新廣播
            micropython.schedule(ble.stack.advertise, _config.adv_interval_us)

        elif event == _IRQ_GATTS_READ_REQUEST:
            conn_handle, value_handle = data

            for c in self._ids.chars:
                if value_handle == c.value_handle:
                    c.on_read(value_handle)
                    return

        elif event == _IRQ_PASSKEY_ACTION:
            conn_handle, action, passkey = data

            if action == _PASSKEY_ACTION_DISPLAY:
                micropython.schedule(_set_passkey, conn_handle)


instance = IdsServer()


def _log_connect(addr_type):
    common.logger.write(
        f"Connected to {ble.utils.addr_to_str(instance.rc_addr)} ({ble.utils.addr_type_to_str(addr_type)})"
    )


def _log_disconnect(addr_type):
    common.logger.write(
        f"Disconnected from {ble.utils.addr_to_str(instance.rc_addr)} ({ble.utils.addr_type_to_str(addr_type)})"
    )


def _set_passkey(conn_handle):
    common.logger.write("Set passkey")
    ble.stack.set_passkey(conn_handle, _PASSKEY_ACTION_DISPLAY, int(_config.passkey))
