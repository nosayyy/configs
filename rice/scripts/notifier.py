#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import threading
import tkinter as tk
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError: 
    import tomli as tomllib

from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, method, signal

DEFAULT_CONFIG = {
    "max_notifications": 5,
    "timeout": 5000,
    "position": "top-right",
    "margin": 10,
    "padding": 10,
    "width": 350,
    "font_family": "Arial",
    "font_size": 12,
    "bg_color": "#2e3440",
    "fg_color": "#d8dee9",
    "border_color": "#4c566a",
    "border_width": 1,
    "corner_radius": 8,
    "close_on_click": True,
    "separator": True,
}


def load_config() -> dict[str, Any]:
    config_path = Path(__file__).with_name("config.toml")
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    section = data.get("notifier", {}) if isinstance(data, dict) else {}
    if not isinstance(section, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(section)
    return merged


config = load_config()


class NotificationDaemon:
    def __init__(self, config) -> None:
        self.config = config
        try:
            self._root = tk.Tk()
        except tk.TclError as exc:
            raise RuntimeError(f"unable to initialize Tk: {exc}") from exc
        self._root.withdraw()
        self._screen_w = self._root.winfo_screenwidth()
        self._screen_h = self._root.winfo_screenheight()
        self._windows: dict[int, tuple[tk.Toplevel, tk.Canvas, int | None]] = {}
        self._history: list[tuple[int, str, str, int]] = []
        self._iface = NotificationsInterface(self)

    def _draw_rounded_rect(self, canvas: tk.Canvas, width: int, height: int, radius: int, fill: str, outline: str) -> None:
        canvas.create_polygon(
            radius, 0,
            width - radius, 0,
            width, 0,
            width, radius,
            width, height - radius,
            width, height,
            width - radius, height,
            radius, height,
            0, height,
            0, height - radius,
            0, radius,
            0, 0,
            radius, 0,
            smooth=True,
            splinesteps=16,
            fill=fill,
            outline=outline,
            width=self.config["border_width"],
            tags="bg",
        )

    def _reposition(self) -> None:
        position = self.config["position"]
        margin = self.config["margin"]
        gap = 6
        width = self.config["width"]
        x = self._screen_w - width - margin if "right" in position else margin
        y = margin if "top" in position else self._screen_h - margin

        for nid in list(self._windows):
            toplevel, canvas, _ = self._windows[nid]
            height = canvas.winfo_height()
            if "bottom" in position:
                y -= height + gap
                toplevel.geometry(f"{width}x{height}+{x}+{y}")
            else:
                toplevel.geometry(f"{width}x{height}+{x}+{y}")
                y += height + gap

    def _close(self, nid: int, reason: int = 2) -> None:
        if nid not in self._windows:
            return
        toplevel, _, after_id = self._windows.pop(nid)
        if after_id is not None:
            toplevel.after_cancel(after_id)
        toplevel.destroy()
        self._iface.NotificationClosed(nid, reason)
        self._reposition()

    @staticmethod
    def _strip_markup(text: str) -> str:
        text = text.replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("<b>", "").replace("</b>", "")
        text = text.replace("<i>", "").replace("</i>", "")
        return text

    def _create_notification(self, nid: int, summary: str, body: str, hints: dict[str, Any], expire: int) -> None:
        urgency = 1
        if "urgency" in hints:
            try:
                urgency = int(hints["urgency"].value)
            except Exception:
                pass

        self._history.append((nid, summary, body, urgency))
        if len(self._history) > 20:
            self._history.pop(0)

        while len(self._windows) >= self.config["max_notifications"]:
            oldest = min(self._windows)
            self._close(oldest, reason=1)

        pad = self.config["padding"]
        width = self.config["width"]
        bg = self.config["bg_color"]
        fg = self.config["fg_color"]
        border = self.config["border_color"]
        font = (self.config["font_family"], self.config["font_size"])
        title_font = (self.config["font_family"], self.config["font_size"], "bold")

        toplevel = tk.Toplevel(self._root)
        toplevel.overrideredirect(True)
        toplevel.attributes("-topmost", True)
        toplevel.attributes("-alpha", 0.95)

        canvas = tk.Canvas(toplevel, width=width, highlightthickness=0, bg=bg)
        canvas.pack(fill=tk.BOTH, expand=True)

        icon_x = pad + 16
        canvas.create_oval(icon_x - 14, pad, icon_x + 14, pad + 28, fill=border, outline="")
        text_x = icon_x + 28
        canvas.create_text(text_x, pad, text=summary, anchor=tk.NW, fill=fg, font=title_font, width=width - text_x - pad)

        body_item = canvas.create_text(
            text_x,
            pad + self.config["font_size"] + 6,
            text=self._strip_markup(body),
            anchor=tk.NW,
            fill=fg,
            font=font,
            width=width - text_x - pad,
        )

        bbox = canvas.bbox(body_item)
        height = max(bbox[3] + pad, pad + 48) if bbox else pad + 48

        if self.config["separator"]:
            canvas.create_line(pad, height - 1, width - pad, height - 1, fill=border, width=1)
            height += 1

        canvas.config(height=height)
        toplevel.geometry(f"{width}x{height}")
        self._draw_rounded_rect(canvas, width, height, self.config["corner_radius"], bg, border)
        canvas.tag_lower("bg")

        canvas.create_text(width - pad - 2, pad, text="×", fill=fg, font=(self.config["font_family"], self.config["font_size"] + 2), tags="close")
        canvas.tag_bind("close", "<Button-1>", lambda _event: self._close(nid, reason=2))

        if self.config["close_on_click"]:
            canvas.bind("<Button-1>", lambda _event: self._close(nid, reason=2))

        timeout = expire if expire >= 0 else self.config["timeout"]
        after_id: int | None = None

        def on_enter(_event: tk.Event) -> None:
            nonlocal after_id
            if after_id is not None:
                toplevel.after_cancel(after_id)
                after_id = None

        def on_leave(_event: tk.Event) -> None:
            nonlocal after_id
            if timeout > 0 and urgency < 2:
                after_id = toplevel.after(timeout, lambda: self._close(nid, reason=1))

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        if timeout > 0 and urgency < 2:
            after_id = toplevel.after(timeout, lambda: self._close(nid, reason=1))

        self._windows[nid] = (toplevel, canvas, after_id)
        self._reposition()

    async def _dbus_loop(self) -> None:
        bus = await MessageBus().connect()
        await bus.request_name("org.freedesktop.Notifications")
        bus.export("/org/freedesktop/Notifications", self._iface)
        while True:
            await asyncio.sleep(3600)

    def _run_dbus(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._dbus_loop())

    def run(self) -> None:
        threading.Thread(target=self._run_dbus, daemon=True).start()
        self._root.mainloop()


class NotificationsInterface(ServiceInterface):
    def __init__(self, daemon: NotificationDaemon) -> None:
        super().__init__("org.freedesktop.Notifications")
        self._daemon = daemon
        self._next_id = 1

    @method()
    def Notify(self, app_name: "s", replaces_id: "u", app_icon: "s", summary: "s", body: "s", actions: "as", hints: "a{sv}", expire_timeout: "i") -> "u":
        if replaces_id > 0:
            nid = replaces_id
            if nid in self._daemon._windows:
                self._daemon._close(nid, reason=2)
        else:
            nid = self._next_id
            self._next_id += 1

        self._daemon._root.after(0, lambda: self._daemon._create_notification(nid, summary, body, hints, expire_timeout))
        return nid

    @method()
    def CloseNotification(self, id: "u") -> "":
        self._daemon._root.after(0, lambda: self._daemon._close(id, reason=3))
        return ""

    @method()
    def GetCapabilities(self) -> "as":
        return ["body", "body-markup", "icon-static", "persistence"]

    @method()
    def GetServerInformation(self) -> "ssss":
        return ["pynotifyd", "pynotifyd", "1.0", "1.2"]

    @signal()
    def NotificationClosed(self, id: "u", reason: "u") -> "uu":
        pass

    @signal()
    def ActionInvoked(self, id: "u", action_key: "s") -> "us":
        pass


class NotifierApp:
    def __init__(self) -> None:
        self.config = dict(config)

    def run(self, argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(description="Notification daemon")
        parser.add_argument("--max", type=int, default=self.config["max_notifications"], help="Maximum visible notifications")
        parser.add_argument("--timeout", type=int, default=self.config["timeout"], help="Default timeout in milliseconds")
        parser.add_argument("--position", choices=["top-right", "top-left", "bottom-right", "bottom-left"], default=self.config["position"], help="Notification anchor position")
        parser.add_argument("--width", type=int, default=self.config["width"], help="Notification width")
        parser.add_argument("--no-separator", action="store_true", help="Disable separator line")
        parser.add_argument("--no-click-close", action="store_true", help="Disable close on click")
        args = parser.parse_args(argv)

        self.config.update({
            "max_notifications": args.max,
            "timeout": args.timeout,
            "position": args.position,
            "width": args.width,
            "separator": not args.no_separator,
            "close_on_click": not args.no_click_close,
        })

        try:
            NotificationDaemon(self.config).run()
            return 0
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            print(f"notifier: {exc}", file=sys.stderr)
            return 1


def main() -> None:
    raise SystemExit(NotifierApp().run())


if __name__ == "__main__":
    main()
