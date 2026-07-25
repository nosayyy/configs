#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from dbus_fast import Message, MessageType, Variant
from dbus_fast.aio import MessageBus

DEFAULT_CONFIG = {
    "default_mode": "area",
    "delay": 0,
}


def load_config() -> dict[str, Any]:
    config_path = Path(__file__).with_name("config.toml")
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    section = data.get("screenshot", {}) if isinstance(data, dict) else {}
    if not isinstance(section, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(section)
    return merged


config = load_config()


class ScreenshotError(Exception):
    pass


class ScreenshotService:
    def __init__(self) -> None:
        self.session = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if not self.session:
            self.session = "wayland" if os.environ.get("WAYLAND_DISPLAY") else (
                "x11" if os.environ.get("DISPLAY") else "unknown"
            )

    @staticmethod
    def _find_command(name: str) -> bool:
        return shutil.which(name) is not None

    def take(self, mode: str, output: Path, delay: int, clipboard: bool) -> Path:
        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)

        if delay > 0:
            time.sleep(delay)

        if mode == "fullscreen":
            self._portal_screenshot(output, interactive=False, modal=False)
        elif mode == "window":
            self._portal_screenshot(output, interactive=False, modal=True)
        else:
            try:
                self._portal_screenshot(output, interactive=True, modal=False)
            except Exception:
                self._area_overlay(output)

        if not output.exists():
            raise ScreenshotError("Screenshot failed")

        if clipboard:
            self._copy_clip(output)

        return output

    def _run(self, command: list[str], input_data: bytes | None = None) -> str:
        result = subprocess.run(command, capture_output=True, text=True, input=input_data)
        if result.returncode != 0:
            raise ScreenshotError(result.stderr.strip() or f"Command failed: {' '.join(command)}")
        return result.stdout.strip()

    def _portal_screenshot(self, out: Path, interactive: bool = True, modal: bool = False) -> None:
        async def grab() -> None:
            bus = await MessageBus().connect()
            token = uuid.uuid4().hex.replace("-", "_")
            sender = bus.unique_name[1:].replace(".", "_")
            options = {
                "handle_token": Variant("s", token),
                "interactive": Variant("b", interactive),
                "modal": Variant("b", modal),
            }
            message = await bus.call(
                Message(
                    destination="org.freedesktop.portal.Desktop",
                    path="/org/freedesktop/portal/desktop",
                    interface="org.freedesktop.portal.Screenshot",
                    member="Screenshot",
                    signature="sa{sv}",
                    body=["", options],
                )
            )

            if message.message_type == MessageType.ERROR:
                raise ScreenshotError(str(message.body[0]))

            request_handle = message.body[0]
            future = asyncio.get_event_loop().create_future()

            def on_response(event_message):
                if event_message.path == request_handle and event_message.member == "Response":
                    future.set_result(event_message.body)

            bus.add_message_handler(on_response)
            try:
                response, results = await asyncio.wait_for(future, timeout=30)
            finally:
                bus.remove_message_handler(on_response)

            if response != 0:
                raise ScreenshotError("Screenshot cancelled or failed")

            uri = results.get("uri")
            if not uri:
                raise ScreenshotError("No uri returned from portal")

            src = uri[7:] if uri.startswith("file://") else uri
            shutil.copy2(src, out)

        asyncio.run(grab())

    def _area_overlay(self, out: Path) -> None:
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        overlay = tk.Toplevel(root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{width}x{height}+0+0")
        overlay.attributes("-alpha", 0.25)
        overlay.configure(bg="black")
        overlay.lift()
        overlay.attributes("-topmost", True)

        canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, cursor="crosshair")
        canvas.pack(fill=tk.BOTH, expand=True)

        selection: dict[str, int | bool] = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "dragging": False}
        rect_id: int | None = None

        def on_press(event: tk.Event) -> None:
            nonlocal rect_id
            selection["x1"] = event.x
            selection["y1"] = event.y
            selection["dragging"] = True
            rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="#ff5555", width=2)

        def on_drag(event: tk.Event) -> None:
            if selection["dragging"] and rect_id is not None:
                canvas.coords(rect_id, selection["x1"], selection["y1"], event.x, event.y)

        def on_release(event: tk.Event) -> None:
            selection["x2"] = event.x
            selection["y2"] = event.y
            selection["dragging"] = False
            overlay.destroy()
            root.update()
            try:
                self._portal_screenshot(out, interactive=False, modal=False)
            finally:
                root.destroy()

        def on_cancel(_: tk.Event) -> None:
            overlay.destroy()
            root.destroy()
            raise ScreenshotError("Screenshot cancelled")

        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", on_cancel)

        root.mainloop()

    def _copy_clip(self, path: Path) -> None:
        data = path.read_bytes()
        if self.session == "wayland" and self._find_command("wl-copy"):
            subprocess.run(["wl-copy"], input=data, check=True)
            return
        if self._find_command("xclip"):
            subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(path)], check=True)
            return
        if self._find_command("xsel"):
            subprocess.run(["xsel", "--clipboard", "--input"], input=data, check=True)
            return
        raise ScreenshotError("No clipboard helper found (wl-copy, xclip, xsel)")


class ScreenshotApp:
    def run(self, argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Screenshot utility")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--fullscreen", action="store_true", help="Capture fullscreen")
        group.add_argument("-a", "--area", action="store_true", help="Capture area (default)")
        group.add_argument("-w", "--window", action="store_true", help="Capture window")
        parser.add_argument("-d", "--delay", type=int, default=config["delay"], help="Delay before capture")
        parser.add_argument("-c", "--clipboard", action="store_true", help="Copy screenshot to clipboard")
        parser.add_argument("-o", "--output", help="Output file path")
        args = parser.parse_args(argv)

        mode = config["default_mode"]
        if args.fullscreen:
            mode = "fullscreen"
        elif args.window:
            mode = "window"

        output = Path(args.output) if args.output else Path(self._default_filename())

        try:
            screenshot = ScreenshotService().take(mode, output, args.delay, args.clipboard)
            print(screenshot)
            return 0
        except ScreenshotError as exc:
            print(f"screenshot: {exc}", file=sys.stderr)
            return 1

    @staticmethod
    def _default_filename() -> str:
        return datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")


def main() -> None:
    raise SystemExit(ScreenshotApp().run())


if __name__ == "__main__":
    main()
