from libqtile import widget
from libqtile.lazy import lazy

from ..settings import (
    BG, FG, SEP_COLOR, INACTIVE_WS, URGENT_BORDER, LOW_BATTERY,
    FONT_SIZE, wlan_interface
)


def make_widgets():
    """Create widget list for the status bar"""

    sep = lambda: widget.Sep(
        linewidth  = 1,
        padding    = 6,
        foreground = SEP_COLOR, 
        background = BG
        )

    return [
        # Батарея
        widget.Battery(
            battery         = 0,
            background      = BG,
            foreground      = FG,
            format          = "  {percent:2.0%}",
            show_short_text = False,
            low_percentage  = 0.2,
            low_foreground  = LOW_BATTERY,
            update_interval = 30,
        ),

        # Трей
        widget.Systray(
            background = BG,
            icon_size  = 14
        ),

        sep(),

        # Громкость
        widget.PulseVolume(
            background      = BG,
            foreground      = FG,
            fmt             = "  {}",
            update_interval = 1,
            mouse_callbacks = {"Button1": lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")},
        ),

        sep(),

        # Вай-фай
        widget.Wlan(
            interface            = wlan_interface,
            background           = BG,
            foreground           = FG,
            format               = "  {essid}",
            disconnected_message = "  off",
            update_interval      = 5,
        ),

        widget.Spacer(),

        # Часы
        widget.Clock(
            format               = "%H:%M",
            background           = BG,
            foreground           = FG,
            fontsize             = FONT_SIZE + 2,
            mouse_callbacks      = {"Button1": lazy.spawn("zenity --calendar")}
        ),

        widget.Spacer(),

        # Рабочие столы
        widget.GroupBox(
            background                 = BG,
            foreground                 = FG,
            active                     = FG,
            inactive                   = INACTIVE_WS,
            highlight_method           = "line",
            urgent_border              = URGENT_BORDER,
            this_current_screen_border = FG,
            disable_drag               = True,
            fontsize                   = FONT_SIZE - 1,
        ),
    ]