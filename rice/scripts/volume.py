#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
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
    "title": "Volume",
    "geometry": "420x140",
    "min_percent": 0,
    "max_percent": 150,
    "default_control": "Master",
}


def load_config() -> dict[str, Any]:
    config_path = Path(__file__).with_name("config.toml")
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    section = data.get("volume", {}) if isinstance(data, dict) else {}
    if not isinstance(section, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(section)
    return merged


config = load_config()


@dataclass
class VolumeState:
    percent: int
    muted: bool


class VolumeManager:
    def __init__(self, control: str) -> None:
        self.control = control
        self.backend = self._detect_backend()

    @staticmethod
    def _has_command(name: str) -> bool:
        return shutil.which(name) is not None

    def _detect_backend(self) -> str:
        if self._has_command("pactl"):
            return "pactl"
        if self._has_command("amixer"):
            return "amixer"
        raise RuntimeError("No supported volume backend found (pactl or amixer required)")

    def _run(self, command: list[str]) -> str:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(command)}")
        return result.stdout

    def get_status(self) -> VolumeState:
        if self.backend == "pactl":
            return self._pulse_status()
        return self._alsa_status()

    def _pulse_status(self) -> VolumeState:
        mute_output = self._run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"])
        volume_output = self._run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"])
        muted = "yes" in mute_output.lower()
        match = re.search(r"(\d+)%", volume_output)
        percent = int(match.group(1)) if match else 0
        return VolumeState(percent=percent, muted=muted)

    def _alsa_status(self) -> VolumeState:
        output = self._run(["amixer", "get", self.control])
        matches = re.findall(r"\[(\d{1,3})%\].*?\[(on|off)\]", output)
        if not matches:
            return VolumeState(percent=0, muted=False)
        percent = int(matches[-1][0])
        muted = matches[-1][1].lower() == "off"
        return VolumeState(percent=percent, muted=muted)

    @staticmethod
    def _clamp(value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))

    def set_volume(self, percent: int) -> VolumeState:
        percent = self._clamp(percent, config["min_percent"], config["max_percent"])
        if self.backend == "pactl":
            self._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])
        else:
            self._run(["amixer", "set", self.control, f"{percent}%"])
        return self.get_status()

    def change_volume(self, delta: int) -> VolumeState:
        current = self.get_status().percent
        return self.set_volume(current + delta)

    def mute(self, enable: bool) -> VolumeState:
        if self.backend == "pactl":
            self._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "yes" if enable else "no"])
        else:
            self._run(["amixer", "set", self.control, "mute" if enable else "unmute"])
        return self.get_status()

    def toggle_mute(self) -> VolumeState:
        state = self.get_status()
        return self.mute(not state.muted)


class VolumeUI:
    def __init__(self, manager: VolumeManager, config) -> None:
        self.tk = tk
        self.manager = manager
        self.config = config
        self.root = tk.Tk()
        self.root.title(self.config["title"])
        self.root.geometry(self.config["geometry"])
        self.root.resizable(False, False)

    def run(self) -> None:
        tk = self.tk
        state = self.manager.get_status()

        label_text = tk.StringVar(value=self._format_state(state))
        label = tk.Label(self.root, textvariable=label_text, font=("Arial", 14))
        label.pack(pady=(12, 8), padx=12)

        slider = tk.Scale(
            self.root,
            from_=self.config["min_percent"],
            to=self.config["max_percent"],
            orient="horizontal",
            length=360,
            showvalue=False,
            command=lambda value: self._on_slider(value, label_text),
        )
        slider.set(state.percent)
        slider.pack(padx=12, pady=(0, 8))

        button_frame = tk.Frame(self.root)
        tk.Button(button_frame, text="Toggle Mute", command=lambda: self._on_toggle(label_text, slider)).pack(side="left", padx=6)
        tk.Button(button_frame, text="Refresh", command=lambda: self._refresh(label_text, slider)).pack(side="left", padx=6)
        tk.Button(button_frame, text="Close", command=self.root.destroy).pack(side="left", padx=6)
        button_frame.pack(pady=(0, 12))

        self.root.mainloop()

    def _on_slider(self, value: str, label_text: "tk.StringVar") -> None:
        try:
            state = self.manager.set_volume(int(float(value)))
            label_text.set(self._format_state(state))
        except Exception as exc:
            label_text.set(str(exc))

    def _on_toggle(self, label_text: "tk.StringVar", slider: "tk.Scale") -> None:
        state = self.manager.toggle_mute()
        label_text.set(self._format_state(state))
        slider.set(state.percent)

    def _refresh(self, label_text: "tk.StringVar", slider: "tk.Scale") -> None:
        state = self.manager.get_status()
        label_text.set(self._format_state(state))
        slider.set(state.percent)

    @staticmethod
    def _format_state(state: VolumeState) -> str:
        return f"{state.percent}% {'(muted)' if state.muted else ''}".strip()


class VolumeApp:
    def run(self, argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Volume controller")
        parser.add_argument("--control", default=config["default_control"], help="ALSA mixer control name")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--set", type=int, metavar="PERCENT", help="Set volume percent")
        group.add_argument("--up", type=int, metavar="PERCENT", help="Increase volume percent")
        group.add_argument("--down", type=int, metavar="PERCENT", help="Decrease volume percent")
        parser.add_argument("--mute", action="store_true", help="Mute audio")
        parser.add_argument("--unmute", action="store_true", help="Unmute audio")
        parser.add_argument("--toggle", action="store_true", help="Toggle mute")
        parser.add_argument("--status", action="store_true", help="Show current volume")
        parser.add_argument("--gui", action="store_true", help="Open volume GUI")
        args = parser.parse_args(argv)

        try:
            manager = VolumeManager(args.control)
        except RuntimeError as exc:
            print(f"volume: {exc}", file=sys.stderr)
            return 1

        if args.gui:
            try:
                VolumeUI(manager, dict(config)).run()
                return 0
            except Exception as exc:
                print(f"volume: GUI error: {exc}", file=sys.stderr)
                return 1

        if args.set is not None:
            self._print_state(manager.set_volume(args.set))
            return 0

        if args.up is not None:
            self._print_state(manager.change_volume(args.up))
            return 0

        if args.down is not None:
            self._print_state(manager.change_volume(-args.down))
            return 0

        if args.mute:
            self._print_state(manager.mute(True))
            return 0

        if args.unmute:
            self._print_state(manager.mute(False))
            return 0

        if args.toggle:
            self._print_state(manager.toggle_mute())
            return 0

        self._print_state(manager.get_status())
        return 0

    @staticmethod
    def _print_state(state: VolumeState) -> None:
        print(f"{state.percent}% {'(muted)' if state.muted else ''}".strip())


def main() -> None:
    raise SystemExit(VolumeApp().run())


if __name__ == "__main__":
    main()
