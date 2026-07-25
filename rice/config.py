                                                                 
#   _____             _   _                ___          _           
#  |     |___ ___ ___| |_|_|___ ___    ___|  _|   ___ _| |___ _____ 
#  |   --|  _| -_| .'|  _| | . |   |  | . |  _|  | .'| . | .'|     |
#  |_____|_| |___|__,|_| |_|___|_|_|  |___|_|    |__,|___|__,|_|_|_|                                                                 

import os
import sys
from pathlib import Path

from libqtile.config import Group, Key, Match, Screen, Click, Drag
from libqtile.dgroups import simple_key_binder
from libqtile.utils import guess_terminal
from libqtile.lazy import lazy

from libqtile import bar, layout, widget

config_dir = Path(__file__).resolve().parent
if str(config_dir) not in sys.path:
    sys.path.insert(0, str(config_dir))

# ---[Params]---------------------------------------------╮

mod = "mod4"
alt = "mod1"

terminal     = guess_terminal()
browser      = "ungoogled-chromium"
file_manager = "pcmanfm"

scripts_dir    = os.path.expanduser("~/.config/qtile/scripts")
wallpaper_path = os.path.expanduser("~/Pictures/wallpaper.jpeg")

volume_cmd     = f"{sys.executable} {scripts_dir}/volume.py"
launcher_cmd   = f"{sys.executable} {scripts_dir}/launcher.py"
notifier_cmd   = f"{sys.executable} {scripts_dir}/notifier.py"
brightness_cmd = f"{sys.executable} {scripts_dir}/brightness.py"
screenshot_cmd = f"{sys.executable} {scripts_dir}/screenshot.py"

bar_size      = 22
font_size     = 12
font_family   = "jetbrains mono"
fg            = "#ffffff"
bg            = "#000000"
sep_color     = "#333333"
inactive_ws   = "#555555"
urgent_border = "#ff5555"
low_battery   = "#ff5555"

# --------------------------------------------------------╯

keys = [
    Key([mod], "t", lazy.spawn(terminal)),
    Key([mod], "d", lazy.spawn(launcher_cmd)),
    Key([mod], "b", lazy.spawn(browser)),
    Key([mod, "shift"], "Return", lazy.spawn(file_manager)),

    Key([mod, "shift"], "r", lazy.reload_config()),

    Key([mod], "q", lazy.window.kill()),

    Key([mod], "Left",  lazy.layout.left()),
    Key([mod], "Down",  lazy.layout.down()),
    Key([mod], "Up",    lazy.layout.up()),
    Key([mod], "Right", lazy.layout.right()),

    Key([mod, "shift"], "Left",  lazy.layout.shuffle_left()),
    Key([mod, "shift"], "Down",  lazy.layout.shuffle_down()),
    Key([mod, "shift"], "Up",    lazy.layout.shuffle_up()),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right()),

    Key([mod, "control"], "Left",  lazy.layout.grow_left()),
    Key([mod, "control"], "Down",  lazy.layout.grow_down()),
    Key([mod, "control"], "Up",    lazy.layout.grow_up()),
    Key([mod, "control"], "Right", lazy.layout.grow_right()),

    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "g", lazy.window.toggle_floating()),

    Key([mod], "Tab",          lazy.next_layout()),
    Key([mod, "shift"], "Tab", lazy.prev_layout()),

    Key([mod], "space",  lazy.widget["keyboardlayout"].next_keyboard()),

    Key([mod], "n",          lazy.group["new"].toscreen()),
    Key([mod, "shift"], "n", lazy.window.togroup("new")),
    Key([mod, "shift"], "d", lazy.group.remove_active_group()),

    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")),
    Key([], "XF86AudioMute",        lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")),

    Key([], "XF86MonBrightnessUp",   lazy.spawn(f"{brightness_cmd} up")),
    Key([], "XF86MonBrightnessDown", lazy.spawn(f"{brightness_cmd} down")),

    Key([mod], "Print",          lazy.spawn(f"{screenshot_cmd} full")),
    Key([mod, "shift"], "Print", lazy.spawn(f"{screenshot_cmd} area")),

    Key([mod], "l", lazy.spawn("loginctl lock-session")),
]

mouse = [
    Drag([alt], "Button1", lazy.window.set_position_floating(),
        start=lazy.window.get_position()),

    Drag([alt], "Button3", lazy.window.set_size_floating(),
        start=lazy.window.get_size()),

    Click([alt], "Button2", lazy.window.bring_to_front())
]

layouts = [
    layout.Columns(
        border_focus  = fg,
        border_normal = bg,
        border_width  = 2,
        margin        = 5,
    ),
]

floating_layout = layout.Floating(
    border_focus  = fg,
    border_normal = bg,
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirm"),
        Match(wm_class="dialog"),
        Match(wm_class="download"),
        Match(wm_class="error"),
        Match(wm_class="file_progress"),
        Match(wm_class="notification"),
        Match(wm_class="splash"),
        Match(wm_class="toolbar"),
        Match(wm_class="Yad"),
        Match(title="Picture-in-Picture"),
    ],
)

widgets = [
    widget.GroupBox(
        active                     = inactive_ws,
        inactive                   = inactive_ws,
        this_current_screen_border = fg,
        this_screen_border         = inactive_ws,
        highlight_method           = "text",
        urgent_border              = urgent_border,
        fontsize                   = font_size,
        font                       = font_family,
        background                 = bg,
        foreground                 = fg,
        padding                    = 3,
        margin_y                   = 2,
        borderwidth                = 1,
    ),
    widget.KeyboardLayout(configured_keyboards = ['us','ru'], display_map={'us': 'us', 'ru': 'ru'}),
    widget.Spacer(background = bg),
    widget.Clock(format = "%H:%M", background = bg, foreground = fg, fontsize = font_size, padding = 2),
    widget.Spacer(background = bg),
    widget.Systray(icon_size = 14, background = bg, foreground = fg, fontsize = font_size, padding = 2),
]


dgroups_key_binder = simple_key_binder(mod)
dgroups_app_rules  = []

groups = [
    Group("1"),
    Group("2"),
    Group("3"),
    Group("4"),
]

screens = [
    Screen(
        top=bar.Bar(
            widgets,
            size = bar_size,
            background = bg,
            opacity = 1.0,
            margin = 0,
        ),
        wallpaper      = wallpaper_path,
        wallpaper_mode = "fill",
    )
]

focus_on_window_activation = "smart"

auto_fullscreen = False

follow_mouse_focus = True
bring_front_click  = False
cursor_warp        = False

wmname = "Qtile"



