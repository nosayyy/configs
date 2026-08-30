#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

DEFAULT_CONFIG = {
    "title": "Brightness",
    "geometry": "420x140",
    "min_percent": 0,
    "max_percent": 100,
    "step": 5,
    "backlight_dir": "/sys/class/backlight",
}


def load_config() -> dict[str, Any]:
    config_path = Path(__file__).with_name("config.toml")
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    section = data.get("brightness", {}) if isinstance(data, dict) else {}
    if not isinstance(section, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(section)
    return merged


config = load_config()
BACKLIGHT_DIR = Path(config["backlight_dir"])


@dataclass
class BrightnessDevice:
    name: str
    path: Path
    max_brightness: int
    brightness: int

    def refresh(self) -> None:
        self.brightness = int((self.path / "brightness").read_text().strip())

    def percent(self) -> int:
        return int(round(self.brightness / self.max_brightness * 100))


class BrightnessManager:
    def __init__(self, device_name: str | None = None) -> None:
        self.devices = self._discover_devices()
        self.device = self._choose_device(device_name)
        if self.device is None:
            raise RuntimeError("No backlight device found")

    def _discover_devices(self) -> list[BrightnessDevice]:
        devices: list[BrightnessDevice] = []
        if BACKLIGHT_DIR.exists():
            for entry in sorted(BACKLIGHT_DIR.iterdir()):
                if not entry.is_dir():
                    continue
                brightness_file = entry / "brightness"
                max_file = entry / "max_brightness"
                if not brightness_file.exists() or not max_file.exists():
                    continue
                try:
                    current = int(brightness_file.read_text().strip())
                    maximum = int(max_file.read_text().strip())
                except ValueError:
                    continue
                devices.append(BrightnessDevice(entry.name, entry, maximum, current))
        return devices

    def _choose_device(self, name: str | None) -> BrightnessDevice | None:
        if not self.devices:
            return None
        if name:
            for device in self.devices:
                if device.name == name:
                    return device
        return self.devices[0]

    def status(self) -> str:
        assert self.device is not None
        return f"{self.device.name}: {self.device.percent()}%"

    def set_percent(self, percent: int) -> int:
        assert self.device is not None
        percent = max(config["min_percent"], min(config["max_percent"], percent))
        value = max(1, self.device.max_brightness * percent // 100)
        (self.device.path / "brightness").write_text(str(value))
        self.device.refresh()
        return self.device.percent()

    def change_percent(self, delta: int) -> int:
        return self.set_percent(self.device.percent() + delta)


class BrightnessUI:
    def __init__(self, manager: BrightnessManager, config) -> None:
        self.tk = tk
        self.manager = manager
        self.config = config
        self.root = tk.Tk()
        self.root.title(self.config["title"])
        self.root.geometry(self.config["geometry"])
        self.root.resizable(False, False)

    def run(self) -> None:
        tk = self.tk
        current = self.manager.device.percent()

        label = tk.Label(self.root, text=f"{current}%", font=("Arial", 16))
        label.pack(pady=(14, 8), padx=12)

        slider = tk.Scale(
            self.root,
            from_=self.config["min_percent"],
            to=self.config["max_percent"],
            orient="horizontal",
            length=360,
            showvalue=False,
            command=lambda value: self._on_slider(value, label),
        )
        slider.set(current)
        slider.pack(padx=12, pady=(0, 12))

        buttons = tk.Frame(self.root)
        tk.Button(buttons, text="Refresh", command=lambda: self._refresh(label, slider)).pack(side="left", padx=6)
        tk.Button(buttons, text="Close", command=self.root.destroy).pack(side="left", padx=6)
        buttons.pack(pady=(0, 12))
        self.root.mainloop()

    def _on_slider(self, value: str, label: "tk.Label") -> None:
        try:
            percent = self.manager.set_percent(int(float(value)))
            label.config(text=f"{percent}%")
        except Exception as exc:
            label.config(text=str(exc))

    def _refresh(self, label: "tk.Label", slider: "tk.Scale") -> None:
        self.manager.device.refresh()
        percent = self.manager.device.percent()
        slider.set(percent)
        label.config(text=f"{percent}%")


class BrightnessApp:
    def run(self, argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Brightness controller")
        parser.add_argument("--device", help="Backlight device name")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--set", type=int, metavar="PERCENT", help="Set brightness percent")
        group.add_argument("--up", type=int, metavar="PERCENT", help="Increase brightness percent")
        group.add_argument("--down", type=int, metavar="PERCENT", help="Decrease brightness percent")
        parser.add_argument("--status", action="store_true", help="Show current brightness")
        parser.add_argument("--gui", action="store_true", help="Open brightness GUI")
        args = parser.parse_args(argv)

        try:
            manager = BrightnessManager(args.device)
        except RuntimeError as exc:
            print(f"brightness: {exc}", file=sys.stderr)
            return 1

        if args.gui:
            try:
                BrightnessUI(manager, dict(config)).run()
            except Exception as exc:
                print(f"brightness: GUI error: {exc}", file=sys.stderr)
                return 1
            return 0

        if args.set is not None:
            print(f"{manager.set_percent(args.set)}%")
            return 0

        if args.up is not None:
            print(f"{manager.change_percent(args.up)}%")
            return 0

        if args.down is not None:
            print(f"{manager.change_percent(-args.down)}%")
            return 0

        if args.status:
            print(manager.status())
            return 0

        print(manager.status())
        return 0


def main() -> None:
    raise SystemExit(BrightnessApp().run())


if __name__ == "__main__":
    main()
