from libqtile.config import Key
from libqtile.lazy import lazy

from ..settings import mod, terminal, browser, file_manager, launcher_cmd, BASE_DIR

keys = [
    # Приложения
    Key([mod], "t", lazy.spawn(terminal)),
    Key([mod], "d", lazy.spawn(launcher_cmd)),
    Key([mod], "b", lazy.spawn(browser)),
    Key([mod], "e", lazy.spawn(file_manager)),

    # Окна
    Key([mod], "q", lazy.window.kill()),
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod, "shift"], "Tab", lazy.prev_layout()),

    # Группы
    Key([mod], "n", lazy.group["new"].toscreen()),
    Key([mod, "shift"], "n", lazy.window.togroup("new")),
    Key([mod], "d", lazy.group.remove_active_group()),

    # Громкость
    Key([], "XF86AudioRaiseVolume", lazy.spawn(f"python3 {BASE_DIR}/utils/volume.py up")),
    Key([], "XF86AudioLowerVolume", lazy.spawn(f"python3 {BASE_DIR}/utils/volume.py down")),
    Key([], "XF86AudioMute", lazy.spawn(f"python3 {BASE_DIR}/utils/volume.py mute")),
    Key([mod], "equal", lazy.spawn(f"python3 {BASE_DIR}/utils/volume.py up")),
    Key([mod], "minus", lazy.spawn(f"python3 {BASE_DIR}/utils/volume.py down")),

    # Яркость
    Key([], "XF86MonBrightnessUp", lazy.spawn(f"python3 {BASE_DIR}/utils/brightness.py up")),
    Key([], "XF86MonBrightnessDown", lazy.spawn(f"python3 {BASE_DIR}/utils/brightness.py down")),
    Key([mod], "Up", lazy.spawn(f"python3 {BASE_DIR}/utils/brightness.py up")),
    Key([mod], "Down", lazy.spawn(f"python3 {BASE_DIR}/utils/brightness.py down")),

    # Скриншоты
    Key([mod], "Print", lazy.spawn(f"python3 {BASE_DIR}/utils/screenshot.py full")),
    Key([mod, "shift"], "Print", lazy.spawn(f"python3 {BASE_DIR}/utils/screenshot.py area")),

    # Блокировка
    Key([mod, "ctrl"], "l", lazy.spawn("loginctl lock-session")),

    # Скретчпад
    Key([mod], "F12", lazy.group["scratchpad"].dropdown_toggle("term")),
]