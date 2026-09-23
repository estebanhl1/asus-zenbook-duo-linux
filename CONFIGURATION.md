# Configuración reproducible

Comprobada el 23 de septiembre de 2026 en el ASUS UX8406MA con Fedora/GNOME. Los programas y archivos de servicio del repositorio coincidían byte por byte con los instalados. El usuario confirmó la corrección de F8, F11 y F12. No hay un archivo TOML/JSON separado: los valores actuales están en los scripts indicados aquí.

## Instalar el conjunto completo

Desde una terminal de la sesión GNOME, sin anteponer sudo:

```bash
bash install.sh
```

Este instalador incluye el servicio de pantallas y los atajos, además de las hotkeys. `install.sh displays` instala únicamente el control de pantallas. Consulta [INSTALL.md](INSTALL.md) para todas las opciones.

## Servicios

| Servicio | Ámbito y arranque | Configuración |
|---|---|---|
| `zenbook-duo-hotkeys.service` | Sistema, `multi-user.target` | `duo-hotkeys.py`, instalado en `/usr/local/lib/zenbook-duo-hotkeys/` |
| `zenbook-duo-screen-toggle.service` | Usuario, `graphical-session.target` | `duo-display-watch.py`, instalado en `~/.local/share/zenbook-duo-screen-toggle/` |

El antiguo `zenbook-duo.service` se deshabilita durante la instalación completa para evitar dos observadores de pantalla.

## Atajos persistentes de GNOME

Los registra `setup-hotkey-shortcuts.py`, conservando los otros atajos personalizados existentes.

| Botón | Evento virtual | Atajo GNOME | Acción |
|---|---|---|---|
| Pantalla inferior | KEY_F13 | XF86Tools | Alternar pantalla inferior |
| F8 | KEY_F14 | XF86Launch5 | Intercambiar posiciones de las pantallas internas |
| F12 | KEY_F15 | XF86Launch6 | Abrir Configuración de GNOME |
| F11 | KEY_F16 | XF86Launch7 | Abrir GNOME Caracteres |

Se guardan bajo `/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/`, en `duo-toggle`, `duo-swap`, `duo-settings` y `duo-emoji`.

## Hardware y comportamiento

- USB: `0b05:1b2c`, interfaz 4 y endpoint `0x85`; activa el modo hotkeys al conectarse.
- Bluetooth: `0b05:1b2d`, informes `ABS_MISC`; procesa los eventos especiales sin interceptar la escritura normal.
- Pantallas: superior `eDP-1`, inferior `eDP-2`.
- Al colocar el teclado se apaga la inferior; al retirarlo vuelve al modo automático encendido.
- Los cambios de monitores externos invalidan las posiciones antiguas y se recalcula la inferior.
- El botón manual puede apagar la inferior mientras el teclado está separado. Acoplar o desacoplar restablece el modo automático.
- F8 necesita ambas pantallas activas y el teclado separado. Mutter valida la distribución antes de aplicarla.
- El volumen y el modo de proyección dependen de los eventos nativos; brillo y micrófono se envían como teclas estándar.

## Límites conservados

No se implementa la iluminación del teclado por Bluetooth ni la sincronización del LED de micrófono. F11 abre Caracteres para seleccionar/copiar, no inserta automáticamente un emoji en cualquier aplicación. F12 abre Configuración de GNOME, no MyASUS. Otras distribuciones, distribuciones de pantallas y variantes del modelo requieren pruebas.

## Comprobación después de reiniciar

```bash
systemctl is-active zenbook-duo-hotkeys.service
systemctl --user is-active zenbook-duo-screen-toggle.service
```

El arranque estaba habilitado al revisar la configuración; no se reinició el equipo durante esa revisión.
