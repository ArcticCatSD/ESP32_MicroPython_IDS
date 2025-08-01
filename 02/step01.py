import binascii
import bluetooth


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


def main():
    # 取得系統唯一的 bluetooth.BLE 物件
    ble = bluetooth.BLE()

    # 開啟 BLE radio
    # 在呼叫任何 BLE 方法前，必須先啟用 BLE
    ble.active(True)

    # 取得本地端的藍芽位址及類型
    mac = ble.config("mac")
    print(f"Loacal address: {addr_to_str(mac[1])} ({addr_type_to_str(mac[0])})")


if __name__ == "__main__":
    main()
    print("done")
