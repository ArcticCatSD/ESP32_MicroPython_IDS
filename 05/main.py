# MicroPython modules
import asyncio
import binascii
import bluetooth
import micropython
import struct

# Custom modules
import config

from common import logger


# BLE 事件
_IRQ_CENTRAL_CONNECT = micropython.const(1)
_IRQ_CENTRAL_DISCONNECT = micropython.const(2)
_IRQ_GATTS_READ_REQUEST = micropython.const(4)
_IRQ_PASSKEY_ACTION = micropython.const(31)

# 配對類型
_PASSKEY_ACTION_DISPLAY = micropython.const(3)

# 裝置的 I/O 類型
_IO_CAPABILITY_DISPLAY_ONLY = micropython.const(0)

# Characteristic 的屬性
_FLAG_READ = micropython.const(0x0002)

# Insulin Delivery Service 相關 UUID
_IDS_UUID = micropython.const(0x183A)
_IDD_FEATURES_UUID = micropython.const(0x2B23)


_config = config.get_config()


def addr_to_str(addr: bytes) -> str:
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
        return f"Unknown ({str(addr_type)})"


def build_ids_definition():
    """創建 Insulin Delivery Service Characteristics"""

    ids = bluetooth.UUID(_IDS_UUID)
    features = (bluetooth.UUID(_IDD_FEATURES_UUID), _FLAG_READ)

    return (ids, (features,))


def build_advertising_payload() -> bytes:
    # 廣播內容型態
    ADV_TYPE_FLAGS = 0x01
    ADV_TYPE_UUID16_COMPLETE = 0x3
    ADV_TYPE_APPEARANCE = 0x19

    # LE General Discoverable Mode
    LE_GENERAL_DISC_MODE = 0x02

    BR_EDR_NOT_SUPPORTED = 0x04

    GENERIC_INSULIN_PUMP = 0x0D40

    payload = bytearray()

    append_adv_packet(
        payload,
        ADV_TYPE_FLAGS,
        struct.pack("B", LE_GENERAL_DISC_MODE | BR_EDR_NOT_SUPPORTED),
    )
    append_adv_packet(payload, ADV_TYPE_UUID16_COMPLETE, struct.pack("<H", _IDS_UUID))
    append_adv_packet(
        payload, ADV_TYPE_APPEARANCE, struct.pack("<H", GENERIC_INSULIN_PUMP)
    )

    return payload


def build_scan_response_payload(local_name: str) -> bytes:
    ADV_TYPE_COMPLETE_LOCAL_NAME = 0x09

    payload = bytearray()

    append_adv_packet(payload, ADV_TYPE_COMPLETE_LOCAL_NAME, local_name.encode("utf-8"))

    return payload


def append_adv_packet(payload: bytearray, adv_type: int, value: bytes | bytearray):
    """Advertising payloads are repeated packets of the following form:
    1 byte data length (N + 1)
    1 byte type
    N bytes type-specific data"""

    payload.extend(struct.pack("BB", len(value) + 1, adv_type) + value)


def ble_isr(event, data):
    ble = bluetooth.BLE()

    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, addr_type, addr = data

        logger.write(
            f"Connected to {addr_to_str(addr)} ({addr_type_to_str(addr_type)}): conn_handle({conn_handle})"
        )

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, addr_type, addr = data

        logger.write(
            f"Disconnected from {addr_to_str(addr)} ({addr_type_to_str(addr_type)}): conn_handle({conn_handle})"
        )

        # 要求 MicroPython 在 BLE 中斷後，儘快重新廣播
        micropython.schedule(ble.gap_advertise, _config.adv_interval_us)

    elif event == _IRQ_GATTS_READ_REQUEST:
        conn_handle, value_handle = data

        # 將要回覆的讀取要求寫入 characteristic 裡
        ble.gatts_write(value_handle, _config.idd_features)
        logger.write(f"Send read response: {tuple(_config.idd_features)}")

    elif event == _IRQ_PASSKEY_ACTION:
        conn_handle, action, passkey = data
        logger.write(
            f"PASSKEY_ACTION: conn_handle({conn_handle}), action({action}), passkey({passkey})"
        )

        if action == _PASSKEY_ACTION_DISPLAY:
            micropython.schedule(
                lambda params: ble.gap_passkey(*params),
                (conn_handle, action, int(_config.passkey)),
            )


async def main():
    # 取得系統唯一的 bluetooth.BLE 物件
    ble = bluetooth.BLE()

    #  指定處理 BLE 事件的函數
    ble.irq(ble_isr)

    # 開啟 BLE radio
    # 在呼叫任何 BLE 方法前，必須先啟用 BLE
    ble.active(True)

    # 取得本地端的藍芽位址及類型
    mac = ble.config("mac")
    logger.write(f"Loacal address: {addr_to_str(mac[1])} ({addr_type_to_str(mac[0])})")

    # 啟用安全機制
    ble.config(le_secure=True)
    ble.config(bond=True)
    ble.config(mitm=True)

    # 指定本裝置只能顯示連線密碼
    ble.config(io=_IO_CAPABILITY_DISPLAY_ONLY)

    # 註冊 IDS
    ids = build_ids_definition()
    services = (ids,)
    handles = ble.gatts_register_services(services)
    ids_handles = handles[0]
    logger.write("IDS Characteristic value handles: " + str(ids_handles))

    # 發送廣播
    adv_data = build_advertising_payload()
    resp_data = build_scan_response_payload(_config.local_name)
    ble.gap_advertise(_config.adv_interval_us, adv_data, resp_data=resp_data)

    # 主執行緒會一直等下去
    flag = asyncio.ThreadSafeFlag()
    await flag.wait()


if __name__ == "__main__":
    asyncio.run(main())
    logger.write("done")
