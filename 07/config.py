# MicroPython modules
import json
import os


CONFIG_PATH = "config.json"


class Config:
    def __init__(self):
        self.local_name = "IDS 🍭"
        self.adv_interval_us = 250_000
        self.passkey = "123456"
        self.idd_features = b"\x01\x02\x03"

    def to_dict(self) -> dict[str, str | int | tuple]:
        return {
            "local_name": self.local_name,
            "adv_interval_us": self.adv_interval_us,
            "passkey": self.passkey,
            "idd_features": tuple(self.idd_features),
        }

    @classmethod
    def from_dict(cls, d: dict[str, str | int | tuple]):
        obj = cls()

        obj.local_name = d["local_name"]
        obj.adv_interval_us = d["adv_interval_us"]
        obj.passkey = d["passkey"]
        obj.idd_features = bytes(d["idd_features"])

        return obj


def get_config():
    # MicroPython 沒有 os.path.exists()
    if CONFIG_PATH in os.listdir():
        with open(CONFIG_PATH, encoding="utf-8") as fp:
            data = json.load(fp)

        return Config.from_dict(data)
    else:
        print("No configuration file")
        return Config()
