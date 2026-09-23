#!/usr/bin/python3
"""USB vendor hotkeys for UX8406MA; protocol credited in THIRD_PARTY_NOTICES."""
import select
import threading
import signal
import time
import usb.core
import usb.util
from evdev import UInput, InputDevice, list_devices, ecodes as E

# Standard volume and display-mode keys are emitted by the physical keyboard.
MAP = {16: [E.KEY_BRIGHTNESSDOWN], 32: [E.KEY_BRIGHTNESSUP],
       124: [E.KEY_MICMUTE], 126: [E.KEY_F16],
       134: [E.KEY_F15], 106: [E.KEY_F13], 156: [E.KEY_F14]}
RUNNING = True


def stop(*args):
    global RUNNING
    RUNNING = False


def send(dev, prefix):
    packet = bytes.fromhex(prefix).ljust(16, b'\x00')
    if dev.ctrl_transfer(0x21, 9, 0x035a, 4, packet, timeout=1000) != 16:
        raise RuntimeError('Incomplete USB control transfer')


def serve(dev, ui):
    detached = claimed = False
    try:
        if dev.is_kernel_driver_active(4):
            dev.detach_kernel_driver(4)
            detached = True
        usb.util.claim_interface(dev, 4)
        claimed = True
        send(dev, '5ad04e00')
        print('USB hotkeys enabled', flush=True)
        level, held = 2, None
        while RUNNING:
            try:
                packet = bytes(dev.read(0x85, 64, timeout=500))
            except usb.core.USBTimeoutError:
                continue
            if len(packet) != 6 or packet[0] != 90 or any(packet[2:]):
                continue  # Ignore status/battery reports, never translate them into keys.
            code = packet[1]
            if code == 0:
                held = None
                continue
            if code == held:
                continue
            held = code
            if code == 199:
                level = (level + 1) % 4
                send(dev, f'5abac5c4{level:02x}')
            elif code in MAP:
                emit(ui, code)
    finally:
        try:
            if claimed:
                try:
                    send(dev, '5ad04e01')
                finally:
                    usb.util.release_interface(dev, 4)
        except usb.core.USBError:
            pass
        finally:
            if detached:
                try:
                    dev.attach_kernel_driver(4)
                except usb.core.USBError:
                    pass
            usb.util.dispose_resources(dev)


def emit(ui, code):
    keys = MAP.get(code, [])
    for key in keys:
        ui.write(E.EV_KEY, key, 1)
    ui.syn()
    for key in reversed(keys):
        ui.write(E.EV_KEY, key, 0)
    ui.syn()


def bluetooth():
    devices = {}
    held = {}
    keys = sorted({key for values in MAP.values() for key in values})
    with UInput({E.EV_KEY: keys}, name='Zenbook Duo Bluetooth Special Keys') as ui:
        try:
            last_scan = 0
            while RUNNING:
                if time.monotonic() - last_scan > 2:
                    last_scan = time.monotonic()
                    for path in list_devices():
                        if path in devices:
                            continue
                        device = None
                        try:
                            device = InputDevice(path)
                            caps = device.capabilities(absinfo=False)
                            if (device.info.bustype == 5 and device.info.vendor == 0x0b05
                                    and device.info.product == 0x1b2d
                                    and E.ABS_MISC in caps.get(E.EV_ABS, [])):
                                devices[path] = device
                                print('Bluetooth hotkeys: ' + path, flush=True)
                                device = None
                        except OSError:
                            pass
                        finally:
                            if device is not None:
                                device.close()
                readable, _, _ = select.select(list(devices.values()), [], [], 0.5)
                for device in readable:
                    try:
                        for event in device.read():
                            if event.type != E.EV_ABS or event.code != E.ABS_MISC:
                                continue
                            code = event.value
                            if code == 0:
                                held[device.path] = None
                            elif held.get(device.path) != code:
                                held[device.path] = code
                                if code in MAP:
                                    emit(ui, code)
                    except OSError:
                        devices.pop(device.path, None)
                        held.pop(device.path, None)
                        device.close()
        finally:
            for device in devices.values():
                device.close()


def bluetooth_worker():
    while RUNNING:
        try:
            bluetooth()
        except Exception as error:
            print(f'Bluetooth hotkeys: {error}', flush=True)
            time.sleep(2)


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    worker = threading.Thread(target=bluetooth_worker, daemon=True)
    worker.start()
    keys = sorted({key for values in MAP.values() for key in values})
    with UInput({E.EV_KEY: keys}, name='Zenbook Duo Special Keys') as ui:
        while RUNNING:
            try:
                dev = usb.core.find(idVendor=0x0b05, idProduct=0x1b2c)
                if dev is not None:
                    serve(dev, ui)
            except Exception as error:
                print(f'Hotkeys: {error}', flush=True)
            if RUNNING:
                time.sleep(2)


if __name__ == '__main__':
    main()
