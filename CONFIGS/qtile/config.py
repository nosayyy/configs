
import os, sys
from pathlib import Path

from libqtile import bar, layout, widget

from libqtile.config import Group, Key, Match, Screen, Click, Drag
from libqtile.dgroups import simple_key_binder
from libqtile.utils import guess_terminal
from libqtile.lazy import lazy

config_dir = Path(__file__).resolve().parent
if str(config_dir) not in sys.path:
    sys.path.insert(0, str(config_dir))

# ----[ Params ]--------------------------------------------------╮

mod = "mod4"
alt = "mod1"

terminal = guess_terminal()
browser = "firefox"

scripts_dir = os.path.expanduser("~/.config/qtile/scripts")
scripts = {
    "volume":     f"{sys.executable} {scripts_dir}/volume.py",
    "notifier":   f"{sys.executable} {scripts_dir}/notifier.py",
    "brightness": f"{sys.executable} {scripts_dir}/brightness.py",
}

wallpaper_path = os.path.expanduser("~/Pictures/wallpaper.jpeg")

bar_size = 22

font_size = 13
font_family = "JetBrainsMono NF"

fg = "#ffffff"
bg = "#000000"

sep_color = "#ffffff"

dgroups_key_binder = simple_key_binder(mod) 

focus_on_window_activation = "smart"

auto_fullscreen = False
auto_create_groups = False

follow_mouse_focus = True
bring_front_click = False
cursor_warp = False

wmname = "qtile"

# ----------------------------------------------------------------╯

keys = [
    Key([mod], "t", lazy.spawn(terminal)),
    Key([mod], "b", lazy.spawn(browser)),
    Key([mod], "d", lazy.spawncmd()),

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

    Key([mod], "space",  lazy.widget["keyboardlayout"].next_keyboard()),

    Key([], "XF86AudioRaiseVolume", lazy.spawn(f"{scripts["volume"]} up")),
    Key([], "XF86AudioLowerVolume", lazy.spawn(f"{scripts["volume"]} down")),
    Key([], "XF86AudioMute",        lazy.spawn(f"{scripts["volume"]} mute")),

    Key([], "XF86MonBrightnessUp",   lazy.spawn(f"{scripts["brightness"]} up")),
    Key([], "XF86MonBrightnessDown", lazy.spawn(f"{scripts["brightness"]} down")),

    Key([mod], "l", lazy.spawn("loginctl lock-session")),
]

mouse = [
    Drag([alt], "Button1", lazy.window.set_position_floating(),
        start = lazy.window.get_position()),

    Drag([alt], "Button3", lazy.window.set_size_floating(),
        start = lazy.window.get_size()),

    Click([alt], "Button2", lazy.window.bring_to_front())
]

groups = [
    Group("1"),
    Group("2"),
    Group("3"),
    Group("4"),
]

layouts = [
    layout.Columns(
        border_focus = fg,
        border_normal = bg,
        border_width = 2,
        margin = 5,
        border_on_single=True,
    ),
]

floating_layout = layout.Floating(
    border_focus = fg,
    border_normal = bg,
    float_rules = [*layout.Floating.default_float_rules]
)

widgets = [
    widget.Clock(fontsize=font_size, font=font_family,
                 foreground=fg, background=bg,
                 format="%H:%M", padding=6),
    
    widget.Sep(foreground=sep_color, size_percent=70),
    
    widget.GroupBox(fontsize=font_size, font=font_family,
                    foreground=fg, background=bg,
                    active="#808080", inactive="#808080",
                    this_current_screen_border = "#FFFFFF",
                    highlight_method="text",
                    borderwidth=0, padding=6),

    widget.Spacer(length=bar.STRETCH),

    widget.WindowName(fontsize=font_size, font=font_family,
                      foreground=fg, background=bg,
                      max_chars=50,
                      width=bar.CALCULATED),

    widget.Spacer(length=bar.STRETCH),

    widget.KeyboardLayout(fontsize=font_size - 1, font=font_family,
                          foreground=fg, background=bg,
                          configured_keyboards=["us", "ru"],
                          display_map={'us': 'en', 'ru': 'ru'},
                          padding=4),

    widget.Prompt(fontsize=font_size, font=font_family, 
                  foreground=fg, background=bg, 
                  prompt="run: "),

    widget.Battery(fontsize=font_size, font=font_family,
                   foreground=fg, background=bg,
                   low_percentage=20, format="{percent:2.0%}",
                   update_interval=10, notify_below=20,
                   padding=6),
]

screens = [
    Screen(
        top = bar.Bar(
            widgets,
            background=bg,
            size=bar_size,
            opacity=1.0,
            margin=0,
        ),
        wallpaper = wallpaper_path,
        wallpaper_mode = "fill",
    )
]