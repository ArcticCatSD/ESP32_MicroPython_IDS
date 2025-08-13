import json

import config


def _build_config():
    c = config.Config()

    with open(config.CONFIG_PATH, "w", encoding="utf-8") as fp:
        # MicroPython 不支援這些命名參數
        json.dump(c.to_dict(), fp, ensure_ascii=False, indent=4)


_build_config()
c = config.get_config()
print(c)
