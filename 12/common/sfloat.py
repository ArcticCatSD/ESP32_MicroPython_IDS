# MicroPython modules
import math


# NAN = 0x07FF
NRES = 0x0800
# POS_INFINITY = 0x07FE
# NEG_INFINITY = 0x0802

_MIN_SPECIAL_MANTISSA = 0x07FE
_MAX_MANTISSA = 0x07FF
_MIN_MANTISSA = 0x0800
_MAX_EXPONENT = 7
_MIN_EXPONENT = -8


def sfloat_to_float(value: int) -> float:
    mantissa = value & 0x0FFF
    mantissa -= (mantissa & 0x0800) << 1

    exponent = (value >> 12) & 0x0F
    exponent -= (exponent & 0x08) << 1

    return mantissa * 10**exponent


def float_to_sfloat(value: float) -> int:
    if value == 0:
        return 0

    if value < 0:
        value = -value
        is_negative = True
        mantissa_max = _MIN_MANTISSA
    else:
        is_negative = False
        mantissa_max = _MAX_MANTISSA

    exponent = 0

    # 放大數值，好儘量保存小數部分
    while math.floor(value) != value:
        value_scale_up = value * 10

        if value_scale_up <= mantissa_max and exponent > _MIN_EXPONENT:
            value = value_scale_up
            exponent -= 1
        else:
            break

    # 縮小數值，好讓數值不超出規範
    # 比如 123456.78 轉為 1234.5678 * 10^2
    while value > mantissa_max and exponent < _MAX_EXPONENT:
        value /= 10
        exponent += 1

    # 四捨五入整數部分
    # 比如 value 為 123456.78，
    # 經由前一步驟，value 變為 1234.5678
    # 四捨五入後，value 為 1235
    # 原數值由 123456.78 變為 123500
    mantissa = math.floor(value + 0.5)

    # 處理 SFloat 的特殊值
    if exponent == 0 and mantissa >= _MIN_SPECIAL_MANTISSA:
        exponent = 1

        # mantissa 除以十後四捨五入
        mantissa = (mantissa + 5) // 10

    # 縮小數值，以儲存最少的 mantissa
    # 比如 1000，儲存為 1 * 10^3
    value_scale_down = mantissa
    while True:
        value_scale_down //= 10
        value_round = value_scale_down * 10

        if value_round == mantissa and exponent < _MAX_EXPONENT:
            mantissa = value_scale_down
            exponent += 1
        else:
            break

    if mantissa > mantissa_max:
        return NRES

    elif is_negative:
        mantissa = -mantissa

    return ((exponent & 0x0F) << 12) | (mantissa & 0x0FFF)
