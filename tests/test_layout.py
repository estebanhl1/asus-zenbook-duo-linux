import importlib.util
from pathlib import Path
import unittest
from gi.repository import GLib

spec = importlib.util.spec_from_file_location('watcher', Path(__file__).resolve().parents[1] / 'duo-display-watch.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def state(names):
    monitors, logical = [], []
    positions = {'DP-3': (0, 0), 'eDP-1': (1920, 0), 'eDP-2': (1920, 1080)}
    for name in names:
        identity = (name, 'Test', 'Panel', '0')
        monitors.append((identity, [('1920x1080@60', 1920, 1080, 60., 1., [1.], {'is-current': True})], {}))
        x, y = positions[name]
        logical.append((x, y, 1., 0, name == 'eDP-1', [identity], {}))
    return (1, monitors, logical, {'layout-mode': 1})


class LayoutTests(unittest.TestCase):
    def watcher(self, names):
        w = module.Watcher.__new__(module.Watcher)
        w.saved = None
        w.saved_context = None
        w.call = lambda *args: GLib.Variant('(ua((ssss)a(siiddada{sv})a{sv})a(iiduba(ssss)a{sv})a{sv})', self.variant_state(names))
        return w

    def variant_state(self, names):
        serial, monitors, logical, props = state(names)
        if 'eDP-2' not in names:
            monitors.append(state(['eDP-2'])[1][0])
        monitors = [(i, [(a,b,c,d,e,f,{k: GLib.Variant('b',v) for k,v in p.items()}) for a,b,c,d,e,f,p in modes], p) for i,modes,p in monitors]
        return serial, monitors, logical, {'layout-mode': GLib.Variant('u', 1)}

    def test_docking_preserves_external_and_upper(self):
        w = self.watcher(['DP-3', 'eDP-1', 'eDP-2'])
        _, layout, _ = w.plan(True)
        self.assertEqual([lm[5][0][0] for lm in layout], ['DP-3', 'eDP-1'])
        self.assertEqual([lm[:5] for lm in layout], [(0,0,1.,0,False), (1920,0,1.,0,True)])
        saved = w.saved
        w.call = self.watcher(['DP-3', 'eDP-1']).call
        self.assertEqual(w.plan(False)[1][-1], saved)

    def test_unplug_external_discards_stale_bottom_position(self):
        w = self.watcher(['DP-3', 'eDP-1', 'eDP-2'])
        w.plan(True)
        self.assertEqual(w.saved[0], 1920)
        raw = self.variant_state(['eDP-1'])
        serial, monitors, logical, props = raw
        logical[0] = (0, 0, *logical[0][2:])
        w.call = lambda *args: GLib.Variant(
            '(ua((ssss)a(siiddada{sv})a{sv})a(iiduba(ssss)a{sv})a{sv})',
            (serial, monitors, logical, props))
        _, layout, _ = w.plan(False)
        self.assertEqual(layout[-1][:2], (0, 1080))
        self.assertEqual(layout[0][:2], (0, 0))

    def test_already_enabled_is_noop(self):
        self.assertIsNone(self.watcher(['eDP-1','eDP-2']).plan(False))

    def test_only_active_display_is_protected(self):
        with self.assertRaises(RuntimeError):
            self.watcher(['eDP-2']).plan(True)


if __name__ == '__main__':
    unittest.main()
