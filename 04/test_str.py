import gc

# 使用 utime 和 time 所測得的結果不同
import time

# import utime


def benchmark(text, func, arg1, arg2):
    gc.collect()
    mem_start = gc.mem_free()
    time_start = time.ticks_us()
    # time_start = utime.ticks_us()
    func(arg1, arg2)
    time_end = time.ticks_us()
    # time_end = utime.ticks_us()
    mem_end = gc.mem_free()
    print(
        text,
        "執行時間:",
        time.ticks_diff(time_end, time_start),
        # utime.ticks_diff(time_end, time_start),
        "微秒",
        "耗費記憶體:",
        mem_start - mem_end,
        "bytes",
    )


times = 100


def test_f_str(n, s):
    for i in range(times):
        # t = f"arg ({n}, {s})"
        s = f"arg ({n}, {s})"
        # print(s)


def test_concate(n, s):
    for i in range(times):
        # t = "arg (" + str(n) + ", " + s + ")"
        s = "arg (" + str(n) + ", " + s + ")"
        # print(s)


def test_join(n, s):
    for i in range(times):
        # t = "".join(("arg (", str(n), ", ", s, ")"))
        s = "".join(("arg (", str(n), ", ", s, ")"))
        # print(s)


def test_percent(n, s):
    for i in range(times):
        # t = "".join("arg (%d, %s)" % (n, s))
        s = "".join("arg (%d, %s)" % (n, s))
        # print(s)


benchmark("F-String", test_f_str, 123, "abc")
benchmark("Concate ", test_concate, 123, "abc")
benchmark("Join    ", test_join, 123, "abc")
benchmark("Percent ", test_percent, 123, "abc")
