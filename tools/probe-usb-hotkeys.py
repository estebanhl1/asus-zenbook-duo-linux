#!/usr/bin/env python3
"""Temporarily enable and inspect ASUS UX8406MA USB vendor hotkeys.
Protocol reference: PegasisForever/zenbook-duo-daemon, src/keyboard_usb.rs.
No key injection, display changes, or persistent installation.
"""
import time
import usb.core
import usb.util

KEYS = {0: 'soltar tecla', 199: 'luz del teclado', 16: 'bajar brillo',
        32: 'subir brillo', 156: 'intercambiar pantallas', 124: 'silenciar micrófono',
        126: 'emojis', 134: 'MyASUS', 106: 'alternar pantalla inferior'}


def main():
    dev = usb.core.find(idVendor=0x0b05, idProduct=0x1b2c)
    if dev is None:
        raise SystemExit('Coloca el teclado sobre el equipo para conectarlo por USB.')
    detached = False
    claimed = False
    enabled = False
    try:
        if dev.is_kernel_driver_active(4):
            dev.detach_kernel_driver(4)
            detached = True
        usb.util.claim_interface(dev, 4)
        claimed = True
        packet = bytes.fromhex('5ad04e00000000000000000000000000')
        if dev.ctrl_transfer(0x21, 0x09, 0x035a, 4, packet, timeout=1000) != 16:
            raise RuntimeError('Transferencia USB incompleta')
        enabled = True
        print('Modo hotkeys activado temporalmente durante 40 segundos.', flush=True)
        print('Prueba F1–F12 SIN Fn y el botón de pantalla inferior.\n'
              'Volumen puede actuar normalmente; las otras funciones solo se identifican aquí.\n'
              'Al terminar se vuelve al modo F y se libera la interfaz.', flush=True)
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            try:
                data = bytes(dev.read(0x85, 64, timeout=500))
            except usb.core.USBTimeoutError:
                continue
            if data and data[0] == 0x5a:
                print(KEYS.get(data[1], 'código especial desconocido') if len(data)>1 else 'reporte vacío', data.hex(), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if enabled:
                dev.ctrl_transfer(0x21, 0x09, 0x035a, 4,
                                  bytes.fromhex('5ad04e01000000000000000000000000'), timeout=1000)
        finally:
            try:
                if claimed:
                    usb.util.release_interface(dev, 4)
            finally:
                if detached:
                    dev.attach_kernel_driver(4)
                usb.util.dispose_resources(dev)
        print('Prueba finalizada; interfaz liberada.', flush=True)


if __name__ == '__main__':
    main()
