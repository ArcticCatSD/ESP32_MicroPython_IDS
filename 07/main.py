# MicroPython modules
import asyncio

# Custom modules
import ble.server
import common.logger


async def main():
    server = ble.server.instance
    server.register_services()

    common.logger.write(
        f"IDS value handles: {tuple(c.value_handle for c in server.srvs[0].chars)}"
    )

    # 主執行緒會一直等下去
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
