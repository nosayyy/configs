import subprocess

from libqtile import hook, qtile
from libqtile.dgroups import dgroup

from ..settings import terminal, notifier_cmd


@hook.subscribe.startup_once
def autostart_once():
    """Run once at startup"""
    subprocess.Popen(notifier_cmd.split())


@hook.subscribe.startup
def setup_scratchpad():
    """Setup scratchpad dropdown terminal"""
    qtile.groups_map["scratchpad"] = dgroup.DGroup("scratchpad")
    qtile.groups_map["scratchpad"].dropdown(
        "term",
        terminal + " -e bash",
        width              = 0.6, 
        height             = 0.6, 
        x                  = 0.2, 
        y                  = 0.1,
        opacity            = 1.0,
        on_focus_lost_hide = False,
    )