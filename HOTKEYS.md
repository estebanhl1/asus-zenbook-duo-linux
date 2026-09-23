# Hotkeys USB y Bluetooth (experimental)

El UX8406MA necesita activar el modo especial USB y leer los informes de la interfaz 4, endpoint 0x85. La prueba física confirmó códigos para luz del teclado, brillo, micrófono, emojis y MyASUS. El servicio USB fue probado por el usuario: funcionaba casi todo salvo F8/F11/F12. La revisión actual corrige sus atajos y añade Bluetooth; el usuario confirmó que ahora funciona el 23 de septiembre de 2026.

Desde una terminal GNOME, ejecuta **sin sudo**:

```bash
bash install.sh
```

El instalador solicita sudo para las dependencias Fedora (`python3-pyusb`, `python3-evdev`) y el servicio del sistema. Instala únicamente código local en `/usr/local/lib/zenbook-duo-hotkeys`. Sustituye el antiguo servicio de pantallas `zenbook-duo.service` por el servicio de usuario de este repositorio, preservando el archivo anterior. No cambia sudoers.

Para instalar componentes por separado o ejecutar sin preguntas, consulta [INSTALL.md](INSTALL.md).

## Acciones

- Volumen y modo de proyección: eventos nativos del teclado al activar las hotkeys; pendientes de confirmación física.
- Luz del teclado: recorre apagado/bajo/medio/alto. Parte de un nivel lógico medio; no consulta el nivel físico inicial.
- Brillo de pantalla y silencio de micrófono: eventos estándar para GNOME. No sincroniza por separado el brillo de ambas pantallas ni el LED del micrófono.
- Emojis: abre GNOME Caracteres mediante XF86Launch7.
- MyASUS: abre Configuración de GNOME (MyASUS no se instala).
- Alternar pantalla inferior: atajo XF86Tools, con el teclado separado; el acoplamiento sigue teniendo prioridad.
- Intercambiar pantallas: XF86Launch5, intercambia posiciones de las internas; Mutter verifica el resultado antes de aplicarlo. Solo con ambas activas y teclado separado.
- Fn+F1–F12: quedan a cargo del firmware, sin reasignar las F normales.

**Bluetooth:** se añadió lectura de informes ABS_MISC del teclado ASUS `0b05:1b2d`, basándose en `keyboard_bt.rs` del proyecto de referencia. La escritura normal sigue a cargo de Linux. Se traducen brillo, micrófono, emojis, Configuración y botones de pantalla. La iluminación del teclado por Bluetooth todavía no está implementada. El usuario confirmó el funcionamiento de la actualización; esto no equivale a una prueba exhaustiva de todas las combinaciones de teclas y conexión.

Los eventos Linux F13–F16 se traducen en Fedora a XF86Tools/XF86Launch5/XF86Launch6/XF86Launch7. Los atajos de GNOME utilizan esos nombres.

El servicio solo lee el canal de eventos especiales, no intercepta el teclado alfanumérico. Crea un teclado virtual mediante uinput para las acciones de GNOME. Ignora los informes de estado como `5a3d64010000`.

## Diagnóstico

```bash
sudo systemctl status zenbook-duo-hotkeys.service
sudo journalctl -u zenbook-duo-hotkeys.service -n 40 --no-pager
```

Prueba inicialmente F1–F6 y la tecla de micrófono con el teclado colocado; luego Fn+F1. Repite esta comprobación si cambias de equipo o de versión de GNOME.

## Retirar el servicio USB

```bash
sudo systemctl disable --now zenbook-duo-hotkeys.service
sudo rm /etc/systemd/system/zenbook-duo-hotkeys.service
sudo rm /usr/local/lib/zenbook-duo-hotkeys/duo-hotkeys.py
sudo rmdir /usr/local/lib/zenbook-duo-hotkeys
sudo systemctl daemon-reload
```

Esto conserva el servicio de pantallas y sus atajos. Los atajos `duo-toggle`, `duo-swap` y `duo-settings` se pueden eliminar en Configuración → Teclado → Atajos personalizados.

## Créditos

Protocolo USB y tabla de códigos basados en [PegasisForever/zenbook-duo-daemon](https://github.com/PegasisForever/zenbook-duo-daemon), commit `7955be868aba807b02ec748c02ab537aabec3ada`. Véase su licencia MIT conservada en `third_party/zenbook-duo-daemon/LICENSE` y `THIRD_PARTY_NOTICES.md`.
