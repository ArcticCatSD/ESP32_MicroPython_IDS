import machine


def write(msg: str):
    """不建議在 ISR 內呼叫。"""

    now = machine.RTC().datetime()
    print(
        f"{now[0]}-{now[1]:02d}-{now[2]:02d} "
        f"{now[4]:02d}:{now[5]:02d}:{now[6]:02d}.{now[7]:06d}  "
        f"{msg}"
    )
