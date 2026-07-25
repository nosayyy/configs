#!/usr/bin/env python3

import configparser
import os
import shlex
import signal
import subprocess
import sys
import time
import tkinter as tk
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Callable

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

DEFAULT_CONFIG = {
    "title": "Launcher",
    "geometry": "650x500",
    "topmost": True,
    "stay_open": False,
    "result_limit": 50,
    "font_family": "Arial",
    "font_size": 14,
    "list_font_size": 12,
    "bg_color": "#2e3440",
    "fg_color": "#d8dee9",
    "entry_bg": "#3b4252",
    "entry_fg": "#eceff4",
    "list_bg": "#2e3440",
    "list_fg": "#d8dee9",
    "list_select_bg": "#4c566a",
    "list_select_fg": "#eceff4",
    "padding": 10,
    "cache_dir": str(Path.home() / ".cache/launcher"),
    "cache_ttl": 86400,
    "force_refresh": True,
    "locale": None,
    "desktop_dirs": [
        "/usr/share/applications",
        "/usr/local/share/applications",
        "~/.local/share/applications",
    ],
}


def load_config() -> dict[str, Any]:
    config_path = Path(__file__).with_name("config.toml")
    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(config_path, "rb") as handle:
        data = tomllib.load(handle)

    section = data.get("launcher", {}) if isinstance(data, dict) else {}
    if not isinstance(section, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(section)
    if "cache_dir" in merged:
        merged["cache_dir"] = os.path.expanduser(str(merged["cache_dir"]))
    if "desktop_dirs" in merged and isinstance(merged["desktop_dirs"], list):
        merged["desktop_dirs"] = [os.path.expanduser(str(path)) for path in merged["desktop_dirs"] if isinstance(path, str)]
    return merged


config = load_config()


@dataclass
class Application:
    name: str
    exec_cmd: str
    icon: str = ""
    comment: str = ""
    categories: list[str] = field(default_factory=list)


class DesktopEntryParser:
    @staticmethod
    def parse(file_path: Path, locale: str | None = None) -> Application | None:
        try:
            desktop_config = configparser.ConfigParser(interpolation=None, strict=False)
            desktop_config.optionxform = lambda option: option
            with open(file_path, "r", encoding="utf-8") as f:
                desktop_config.read_file(f)

            if "Desktop Entry" not in desktop_config:
                return None

            entry = desktop_config["Desktop Entry"]

            if entry.get("Type", "").strip() not in ("Application", ""):
                return None

            if entry.get("NoDisplay", "false").lower() == "true" or \
               entry.get("Hidden", "false").lower() == "true":
                return None

            name = DesktopEntryParser._get_localized(entry, "Name", locale)
            if not name:
                name = entry.get("Name", "").strip()
            if not name:
                return None

            exec_cmd = entry.get("Exec", "").strip()
            if not exec_cmd:
                return None

            icon = entry.get("Icon", "").strip()
            comment = DesktopEntryParser._get_localized(entry, "Comment", locale)
            if not comment:
                comment = entry.get("Comment", "").strip()

            categories = [c.strip() for c in entry.get("Categories", "").split(";") if c.strip()]

            return Application(name, exec_cmd, icon, comment, categories)

        except Exception:
            return None

    @staticmethod
    def _get_localized(entry: configparser.SectionProxy, key: str, locale: str | None) -> str:
        if not locale:
            locale = os.environ.get("LANG", "en_US.UTF-8")
        lang_part = locale.split(".")[0]
        candidates = [f"{key}[{lang_part}]"]
        if "_" in lang_part:
            base, country = lang_part.split("_", 1)
            candidates.append(f"{key}[{base}]")
            candidates.append(f"{key}[{base}_{country}]")
        for cand in candidates:
            value = entry.get(cand, "").strip()
            if value:
                return value
        return ""


class ApplicationDatabase:
    def __init__(self, config) -> None:
        self.config = config
        self.cache_dir = Path(config["cache_dir"])
        self.cache_file = self.cache_dir / "apps.json"
        self.applications: list[Application] = []

    def load(self) -> list[Application]:
        if self.config.get("force_refresh", True):
            self._scan_system()
            self._save_cache()
            return self.applications

        if self._load_cache():
            return self.applications

        self._scan_system()
        self._save_cache()
        return self.applications

    def _load_cache(self) -> bool:
        if not self.cache_file.exists():
            return False
        try:
            mtime = self.cache_file.stat().st_mtime
            if time.time() - mtime > self.config.get("cache_ttl", 86400):
                return False
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            self.applications = [Application(**item) for item in data]
            return True
        except Exception:
            return False

    def _save_cache(self) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump([asdict(a) for a in self.applications], f, indent=2)
        except Exception:
            pass

    def _scan_system(self) -> None:
        seen_names = set()
        self.applications = []
        locale = self.config.get("locale")

        for directory in self._get_desktop_dirs():
            if not directory.exists():
                continue
            for desktop_file in directory.glob("*.desktop"):
                app = DesktopEntryParser.parse(desktop_file, locale)
                if app and app.name not in seen_names:
                    seen_names.add(app.name)
                    self.applications.append(app)

        self.applications.sort(key=lambda a: a.name.lower())

    @staticmethod
    def _get_desktop_dirs() -> list[Path]:
        dirs = []
        for path in config.get("desktop_dirs", []):
            if isinstance(path, str):
                dirs.append(Path(path).expanduser())
        xdg_data = os.environ.get("XDG_DATA_DIRS", "")
        for path in xdg_data.split(":"):
            if path:
                dirs.append(Path(path) / "applications")
        return list(dict.fromkeys(dirs))


class SearchEngine:
    @staticmethod
    def search(applications: list[Application], query: str, limit: int) -> list[Application]:
        if not query:
            return applications[:limit]

        query_lower = query.lower()
        scored = []

        for app in applications:
            name_lower = app.name.lower()
            if query_lower in name_lower:
                score = 1.0 / (1 + name_lower.index(query_lower))
                scored.append((score, app))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [app for _, app in scored[:limit]]


class LauncherUI:
    def __init__(self, config,
                 on_search: Callable[[str], list[Application]],
                 on_launch: Callable[[Application], None]) -> None:
        self.config = config
        self.on_search = on_search
        self.on_launch = on_launch

        self.filtered_apps: list[Application] = []

        self.root = tk.Tk()
        self.root.title(config["title"])
        self.root.geometry(config["geometry"])
        self.root.resizable(False, False)
        if config.get("topmost", True):
            self.root.attributes("-topmost", True)

        self._build_widgets()
        self._bind_events()

    def _build_widgets(self) -> None:
        pad = self.config["padding"]
        bg = self.config["bg_color"]
        font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        list_font_size = self.config["list_font_size"]

        self.entry = tk.Entry(
            self.root,
            font=(font_family, font_size),
            bg=self.config["entry_bg"],
            fg=self.config["entry_fg"],
            insertbackground=self.config["entry_fg"],
            relief="flat",
            highlightthickness=0,
        )
        self.entry.pack(fill="x", padx=pad, pady=(pad, pad // 2))
        self.entry.focus_set()

        list_frame = tk.Frame(self.root, bg=bg)
        list_frame.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self.listbox = tk.Listbox(
            list_frame,
            font=(font_family, list_font_size),
            bg=self.config["list_bg"],
            fg=self.config["list_fg"],
            selectbackground=self.config["list_select_bg"],
            selectforeground=self.config["list_select_fg"],
            activestyle="none",
            highlightthickness=0,
            relief="flat",
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=bg)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

    def _bind_events(self) -> None:
        self.entry.bind("<KeyRelease>", self._handle_keypress)
        self.entry.bind("<Return>", self._handle_enter)
        self.entry.bind("<Escape>", lambda e: self.quit())
        self.entry.bind("<Up>", lambda e: self._move_selection(-1))
        self.entry.bind("<Down>", lambda e: self._move_selection(1))
        self.listbox.bind("<Double-Button-1>", self._handle_enter)
        self.listbox.bind("<Return>", self._handle_enter)
        self.root.bind("<Escape>", lambda e: self.quit())

    def _handle_keypress(self, event) -> None:
        if event.keysym in ("Up", "Down", "Left", "Right", "Home", "End", "Page_Up", "Page_Down"):
            return
        query = self.entry.get()
        self._update_list(self.on_search(query))

    def _handle_enter(self, event=None) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        if idx < len(self.filtered_apps):
            self.on_launch(self.filtered_apps[idx])
            if not self.config.get("stay_open", False):
                self.quit()

    def _move_selection(self, delta: int) -> None:
        current = self.listbox.curselection()
        if current:
            idx = current[0] + delta
        else:
            idx = 0 if delta > 0 else self.listbox.size() - 1
        if 0 <= idx < self.listbox.size():
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx)
            self.listbox.see(idx)

    def _update_list(self, apps: list[Application]) -> None:
        self.filtered_apps = apps
        self.listbox.delete(0, "end")
        for app in apps:
            self.listbox.insert("end", app.name)
        if apps:
            self.listbox.selection_set(0)
            self.listbox.see(0)

    def run(self) -> None:
        self.root.mainloop()

    def quit(self) -> None:
        self.root.quit()
        self.root.destroy()


class LauncherApp:
    def __init__(self):
        self.config = config
        self.database = ApplicationDatabase(self.config)
        self.applications = self.database.load()
        self.ui = LauncherUI(
            config=self.config,
            on_search=self._search_applications,
            on_launch=self._launch_application
        )
        self.ui._update_list(self.applications[:self.config["result_limit"]])

    def _search_applications(self, query: str) -> list[Application]:
        return SearchEngine.search(self.applications, query, self.config["result_limit"])

    def _launch_application(self, app: Application) -> None:
        try:
            parts = shlex.split(app.exec_cmd)
            clean_parts = [p for p in parts if not p.startswith("%")]
            if clean_parts:
                subprocess.Popen(clean_parts,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def run(self) -> None:
        self.ui.run()


def main():
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    launcher = LauncherApp()
    launcher.run()


if __name__ == "__main__":
    main()
