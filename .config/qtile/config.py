import sys
from pathlib import Path

from libqtile import bar
from libqtile.config import Screen

CONFIG_DIR = Path(__file__).resolve().parent
if str(CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(CONFIG_DIR))

from settings import (
    BAR_SIZE, BG, WALLPAPER_PATH
)

from core.groups import dgroups_key_binder, dgroups_app_rules, groups
from core.layouts import layouts, floating_layout
from core.widgets import make_widgets
from core.keys import keys
from core import hooks  # noqa: F401

screens = [
    Screen(
        top = bar.Bar(
             make_widgets(),
             size       = BAR_SIZE,
             background = BG,
             opacity    = 1.0,
             margin     = 0
            ),
        
        wallpaper      = WALLPAPER_PATH,
        wallpaper_mode = 'fill'
    )
]

dgroups_key_binder         = dgroups_key_binder
dgroups_app_rules          = dgroups_app_rules
focus_on_window_activation = "smart"
follow_mouse_focus         = True
bring_front_click          = False
auto_fullscreen            = True
cursor_warp                = False
wmname                     = "Qtile"