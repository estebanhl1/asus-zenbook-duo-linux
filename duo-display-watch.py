#!/usr/bin/python3
"""Toggle the covered panel while retaining the current Mutter layout."""
import os
import sys
import time
from pathlib import Path
from gi.repository import Gio, GLib

BUS = 'org.gnome.Mutter.DisplayConfig'
PATH = '/org/gnome/Mutter/DisplayConfig'


def attached():
    for device in Path('/sys/bus/usb/devices').glob('*'):
        try:
            if (device / 'idVendor').read_text().strip() == '0b05' and (device / 'idProduct').read_text().strip() == '1b2c':
                return True
        except FileNotFoundError:
            continue
    return False


class Watcher:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.saved = None
        self.saved_context = None

    def call(self, method, args=None):
        return self.bus.call_sync(BUS, PATH, BUS, method, args, None,
                                  Gio.DBusCallFlags.NONE, 5000, None)

    def plan(self, docked):
        serial, monitors, logical, props = self.call('GetCurrentState').unpack()
        physical = {m[0][0]: m for m in monitors}
        modes = {}
        for name, (_, available, _) in physical.items():
            modes[name] = next((m for m in available if m[6].get('is-current')), None)
        layout = []
        for x, y, scale, transform, primary, specs, _ in logical:
            outputs = []
            for spec in specs:
                name = spec[0]
                p = physical[name][2]
                settings = {key: GLib.Variant('u', p[key]) for key in ('color-mode', 'rgb-range') if key in p}
                outputs.append((name, modes[name][0], settings))
            layout.append((x, y, scale, transform, primary, outputs))
        bottom = next((lm for lm in layout if any(o[0] == 'eDP-2' for o in lm[5])), None)
        context = tuple(
            (lm[:4], tuple((o[0], o[1]) for o in lm[5]))
            for lm in layout if lm is not bottom
        )
        if docked:
            if bottom is None:
                return None
            if len(bottom[5]) != 1:
                raise RuntimeError('Mirrored lower panel: refusing to alter a shared logical monitor')
            remaining = [lm for lm in layout if lm is not bottom]
            if not remaining:
                raise RuntimeError('Refusing to disable the only active display')
            self.saved = bottom
            self.saved_context = context
            if bottom[4]:
                lm = list(remaining[0]); lm[4] = True; remaining[0] = tuple(lm)
            layout = remaining
        else:
            if bottom is not None:
                self.saved = bottom
                self.saved_context = context
                return None
            if 'eDP-2' not in physical:
                return None
            top = next((lm for lm in layout if any(o[0] == 'eDP-1' for o in lm[5])), None)
            if top is None:
                raise RuntimeError('Upper panel inactive: cannot place lower panel safely')
            available = physical['eDP-2'][1]
            if (self.saved and self.saved_context == context
                    and any(m[0] == self.saved[5][0][1] for m in available)):
                bottom = list(self.saved); bottom[4] = False
            else:
                mode = next((m for m in available if m[6].get('is-preferred')), available[0])
                scale = min(mode[5], key=lambda s: abs(s-top[2]))
                upper = modes['eDP-1']
                height = upper[1] if top[3] in (1,3,5,7) else upper[2]
                divisor = top[2] if props.get('layout-mode', 1) == 1 else 1
                bottom = [top[0], top[1] + round(height / divisor), scale, top[3], False, [('eDP-2', mode[0], {})]]
            layout.append(tuple(bottom))
        options = {'layout-mode': GLib.Variant('u', props['layout-mode'])} if 'layout-mode' in props else {}
        return serial, layout, options

    def apply(self, docked, verify=False):
        plan = self.plan(docked)
        if plan is None:
            return
        serial, layout, options = plan
        # Verify first, then apply temporarily; GNOME's saved settings remain intact.
        for method in ([0] if verify else [0, 1]):
            self.call('ApplyMonitorsConfig', GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})', (serial, method, layout, options)))
        print(('Verified' if verify else 'Applied') + (' keyboard docked' if docked else ' keyboard detached'), flush=True)


def main():
    watcher = Watcher()
    if '--verify-docked' in sys.argv:
        watcher.apply(True, verify=True)
        return
    command = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')) / 'zenbook-duo-command'
    if '--toggle' in sys.argv or '--swap' in sys.argv:
        temporary = command.with_name(command.name + f'.{os.getpid()}')
        temporary.write_text('swap' if '--swap' in sys.argv else 'toggle')
        temporary.replace(command)
        return
    manual_off = False
    previous = None
    while True:
        try:
            state = attached()
            if state != previous:
                time.sleep(0.4)
                if state != attached():
                    continue
                manual_off = False
                print(f'Keyboard attached: {state}', flush=True)
            # Reconcile display hotplug and GNOME layout changes even when
            # the keyboard stays detached. plan() is a no-op if already correct.
            if command.exists():
                action = command.read_text().strip()
                command.unlink(missing_ok=True)
                if not state and action == 'toggle':
                    current = watcher.call('GetCurrentState').unpack()[2]
                    manual_off = any(spec[0] == 'eDP-2' for lm in current for spec in lm[5])
                elif not state and action == 'swap':
                    plan = watcher.plan(True)
                    if plan is not None:
                        serial, layout, options = plan
                        bottom = list(watcher.saved)
                        index = next((i for i,lm in enumerate(layout) if any(o[0]=='eDP-1' for o in lm[5])), None)
                        if index is not None:
                            top = list(layout[index])
                            top[:2], bottom[:2] = bottom[:2], top[:2]
                            layout[index] = tuple(top)
                            layout.append(tuple(bottom))
                            for method in (0,1):
                                watcher.call('ApplyMonitorsConfig', GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})', (serial,method,layout,options)))
            watcher.apply(state or manual_off)
            previous = state
        except Exception as error:
            print(f'Display watcher: {error}', file=sys.stderr, flush=True)
        time.sleep(1)


if __name__ == '__main__':
    main()
