#!/usr/bin/env python3
"""Read only function/special key events for 40 seconds; change no settings."""
import os
from pathlib import Path
import re
import selectors
import struct
import time


def main():
    names = {}
    header = Path('/usr/include/linux/input-event-codes.h')
    if header.exists():
        for name, value in re.findall(r'^#define\s+(KEY_\w+)\s+(0x[0-9a-fA-F]+|\d+)\b', header.read_text(), re.M):
            names[int(value, 0)] = name
    event = struct.Struct('@llHHi')
    selector = selectors.DefaultSelector()
    for path in sorted(Path('/sys/class/input').glob('event*')):
        name = (path / 'device/name').read_text().strip()
        if not ('Zenbook Duo Keyboard' in name or name == 'Asus WMI hotkeys'):
            continue
        if 'Mouse' in name or 'Touchpad' in name:
            continue
        device = Path('/dev/input') / path.name
        try:
            stream = device.open('rb', buffering=0)
        except OSError as error:
            print(f'No se pudo abrir {device}: {error}', flush=True)
            continue
        selector.register(stream, selectors.EVENT_READ, (path.name, name))
        print(f'Escuchando {path.name}: {name}', flush=True)
    if not selector.get_map():
        raise SystemExit('No hay dispositivos accesibles. Ejecuta con sudo en la terminal del equipo.')
    print('Durante 40 segundos: F1, F2, F5 sin Fn; luego mantén Fn y pulsa F1, F2, F5.\n'
          'Después pulsa la tecla de luz del teclado y la de cambio de pantalla.\n'
          'No se registran letras ni números. No se bloquean las teclas.', flush=True)
    deadline = time.monotonic() + 40
    count = 0
    try:
        while time.monotonic() < deadline:
            for key, _ in selector.select(timeout=min(1, max(0, deadline-time.monotonic()))):
                data = os.read(key.fileobj.fileno(), event.size * 64)
                if not data:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                for offset in range(0, len(data)-event.size+1, event.size):
                    _, _, kind, code, value = event.unpack_from(data, offset)
                    if kind == 1 and (59 <= code <= 68 or code in (87,88) or 113 <= code < 256 or code >= 352):
                        print(f'{key.data[0]} {names.get(code, "KEY_"+str(code))} value={value}', flush=True)
                        count += 1
    except KeyboardInterrupt:
        pass
    finally:
        for key in list(selector.get_map().values()):
            key.fileobj.close()
        selector.close()
    print(f'Fin. Eventos especiales detectados: {count}', flush=True)


if __name__ == '__main__':
    main()
