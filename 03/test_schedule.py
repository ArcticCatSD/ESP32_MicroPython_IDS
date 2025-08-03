import asyncio
import binascii
import bluetooth
import machine
import micropython
import time


micropython.alloc_emergency_exception_buf(100)


# BLE 事件
_IRQ_CENTRAL_DISCONNECT = micropython.const(2)

# 廣播頻率
_adv_interval_us = 250_000

_rtc = machine.RTC()

_f4_arg = 0


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


def log(msg: str):
    now = _rtc.datetime()
    print(f"{now[4]:02d}:{now[5]:02d}:{now[6]:02d}.{now[7]:06d}  " f"{msg}")


def f1(arg):
    log("f1")


def f2(arg):
    global _f4_arg
    log("f2 blocked")
    _f4_arg += 1
    asyncio.create_task(f4(_f4_arg))
    time.sleep(1)


def f3(arg):
    log("f3")


async def f4(arg):
    log(f"f4 async: {arg}")


def ble_isr(event, data):
    log(f"event: {event}")
    micropython.schedule(f1, None)
    micropython.schedule(f2, None)
    micropython.schedule(f3, None)

    ble = bluetooth.BLE()

    if event == _IRQ_CENTRAL_DISCONNECT:
        micropython.schedule(ble.gap_advertise, _adv_interval_us)


async def main():
    while True:
        log("Main loop")
        await asyncio.sleep_ms(1000)


ble = bluetooth.BLE()
ble.active(True)
mac = ble.config("mac")
print(f"Loacal address: {addr_to_str(mac[1])} ({addr_type_to_str(mac[0])})")
ble.irq(ble_isr)
ble.gap_advertise(_adv_interval_us)
asyncio.run(main())
