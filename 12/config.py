# MicroPython modules
import json
import os


CONFIG_PATH = "config.json"


class Config:
    def __init__(self):
        self.local_name = "IDS 🍭"
        self.adv_interval_us = 250_000
        self.passkey = "123456"

        self.idd_features_insulin_conc = 100
        self.idd_features_flags = 0b_0000_0000_0000_0001_1110_0001
        self._refresh(self.idd_features_flags)

    def _refresh(self, flags):
        self.is_e2e_protection_supported = bool(flags & 0x0001)
        # self.is_basal_rate_supported = bool(flags & 0x0002)
        # self.is_tbr_absolute_supported = bool(flags & 0x0004)
        # self.is_tbr_relative_supported = bool(flags & 0x0008)
        # self.is_tbr_template_supported = bool(flags & 0x0010)
        # self.is_fast_bolus_supported = bool(flags & 0x0020)
        # self.is_extended_bolus_supported = bool(flags & 0x0040)
        # self.is_multiwave_bolus_supported = bool(flags & 0x0080)
        # self.is_bolus_delay_time_supported = bool(flags & 0x0100)
        # self.is_bolus_template_supported = bool(flags & 0x0200)
        # self.is_bolus_activation_type_supported = bool(flags & 0x0400)
        # self.is_multiple_bond_supported = bool(flags & 0x0800)
        # self.is_isf_profile_template_supported = bool(flags & 0x1000)
        # self.is_i2cho_ratio_profile_template_supported = bool(flags & 0x2000)
        # self.is_target_glucose_range_profile_template_supported = bool(flags & 0x4000)
        # self.is_insulin_on_board_supported = bool(flags & 0x8000)

    def to_dict(self) -> dict[str, str | int | tuple]:
        return {
            "local_name": self.local_name,
            "adv_interval_us": self.adv_interval_us,
            "passkey": self.passkey,
            "idd_features_insulin_conc": self.idd_features_insulin_conc,
            "idd_features_flags": self.idd_features_flags,
        }

    @classmethod
    def from_dict(cls, d: dict[str, str | int | tuple]):
        obj = cls()

        obj.local_name = d["local_name"]
        obj.adv_interval_us = d["adv_interval_us"]
        obj.passkey = d["passkey"]

        obj.idd_features_insulin_conc = d["idd_features_insulin_conc"]
        obj.idd_features_flags = d["idd_features_flags"]
        obj._refresh(obj.idd_features_flags)

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
