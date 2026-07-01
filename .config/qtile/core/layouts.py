from libqtile import layout
from libqtile.config import Match

from settings import FG, BG

layouts = [
    layout.Max(),
    layout.MonadTall(),
    layout.MonadWide(),
    layout.Columns(
        border_focus  = FG,
        border_normal = BG,
        border_width  = 2
    ),
]

floating_layout = layout.Floating(
    border_focus  = FG,
    border_normal = BG,
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class = "confirm"            ),
        Match(wm_class = "dialog"             ),
        Match(wm_class = "download"           ),
        Match(wm_class = "error"              ),
        Match(wm_class = "file_progress"      ),
        Match(wm_class = "notification"       ),
        Match(wm_class = "splash"             ),
        Match(wm_class = "toolbar"            ),
        Match(wm_class = "Yad"                ),
        Match(title    = "Picture-in-Picture" ),
    ],
)