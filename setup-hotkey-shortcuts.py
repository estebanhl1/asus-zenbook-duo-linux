#!/usr/bin/python3
import os
from pathlib import Path
from gi.repository import Gio

root = Path.home() / '.local/share/zenbook-duo-screen-toggle'
script = root / 'duo-display-watch.py'
# Fixed executable and quoted file path, no commands received from USB.
quoted = "'" + str(script).replace("'", "'\\''") + "'"
base = '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/'
settings = Gio.Settings.new('org.gnome.settings-daemon.plugins.media-keys')
paths = list(settings.get_strv('custom-keybindings'))
for name, key, command in [('duo-toggle','XF86Tools',f'/usr/bin/python3 {quoted} --toggle'),
                           ('duo-swap','XF86Launch5',f'/usr/bin/python3 {quoted} --swap'),
                           ('duo-settings','XF86Launch6','gnome-control-center'),
                           ('duo-emoji','XF86Launch7','gnome-characters')]:
    path = base + name + '/'
    binding = Gio.Settings.new_with_path('org.gnome.settings-daemon.plugins.media-keys.custom-keybinding', path)
    binding.set_string('name',name)
    binding.set_string('binding',key)
    binding.set_string('command',command)
    if path not in paths:
        paths.append(path)
settings.set_strv('custom-keybindings', paths)
Gio.Settings.sync()
print('Atajos de pantalla y Configuración registrados en GNOME.')
