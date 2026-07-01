from libqtile.config import Group
from libqtile.dgroups import simple_key_binder

from ..settings import mod

dgroups_key_binder = simple_key_binder(mod)
dgroups_app_rules = []

groups = [Group("1")]