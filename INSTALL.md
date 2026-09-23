# Instalación completa y por componentes

## Requisitos

ASUS Zenbook Duo UX8406MA, Fedora Workstation y sesión gráfica GNOME. Ejecuta los comandos como tu usuario habitual, desde una terminal dentro de esa sesión. El instalador comprueba Fedora y la sesión cuando necesita configurar GNOME.

Las dependencias se instalan automáticamente con `dnf -y`, solo cuando faltan. No se descarga ni ejecuta código de otros repositorios. Las utilidades originales de `third_party/` se incluyen como referencia y no se instalan.

## Instalar todo

Descarga y descomprime el repositorio o clónalo. Entra en la carpeta que contiene `install.sh` y ejecuta:

```bash
bash install.sh
```

Sin argumentos equivale a `bash install.sh all`. Instala y activa:

1. Dependencias Python, PyGObject, PyUSB, evdev, Caracteres y Configuración de GNOME.
2. Servicio de usuario para el apagado automático y los botones de pantalla.
3. Atajos F8, F11, F12 y botón de pantalla inferior.
4. Servicio del sistema para hotkeys USB/Bluetooth.
5. Carga de `uinput` ahora y al arrancar.

Deshabilita el antiguo `zenbook-duo.service`, si existe, para evitar dos controladores simultáneos. Conserva ese archivo. Los archivos propios reemplazados reciben copia `.before-FECHA`; también se guarda una exportación de los atajos antes de modificarlos. Los atajos ajenos se conservan.

**No antepongas sudo al instalador completo.** Solo sus operaciones del sistema utilizan sudo. Puede pedir tu contraseña de administrador, pero no pregunta por cada paquete ni presenta menús de configuración.

## Ejecución sin ninguna pregunta

Si la autorización sudo ya está vigente o tu cuenta tiene permisos adecuados:

```bash
bash install.sh --non-interactive
```

Esta opción usa `sudo -n`: si falta autorización, termina con un error en lugar de pedir una contraseña. No guarda contraseñas ni cambia sudoers. Para autorizar una vez y luego ejecutar sin preguntas:

```bash
sudo -v
bash install.sh --non-interactive
```

La primera orden puede pedir la contraseña. Para una instalación realmente desatendida, las autorizaciones deben estar provisionadas previamente. La configuración de GNOME requiere una sesión gráfica de usuario activa; no está diseñado para ejecutarse desde una sesión root o desde un servidor sin escritorio.

## Instalar cada componente por separado

Cada componente instala automáticamente sus dependencias. Para obtener el conjunto completo en pasos separados, usa este orden:

```bash
bash install.sh displays
bash install.sh hotkeys
bash install.sh shortcuts
```

| Opción | Qué instala | Qué no instala |
|---|---|---|
| `displays` | Programa y servicio de usuario para pantallas | Servicio USB/Bluetooth y atajos |
| `hotkeys` | Programa y servicio de sistema USB/Bluetooth, uinput | Servicio de pantallas y atajos GNOME |
| `shortcuts` | Los cuatro atajos GNOME y aplicaciones asociadas | Servicios; exige haber instalado `displays` |
| `dependencies` | Todas las dependencias del conjunto | Programas, servicios y atajos |

Con solo `hotkeys`, las teclas estándar de brillo/micrófono y el control USB de iluminación pueden funcionar, pero F8/F11/F12 y el botón de pantalla necesitan también `shortcuts` y `displays`.

Todas las opciones aceptan `--non-interactive` y `--dry-run`. No se eligen teclas individuales: el componente hotkeys contiene el protocolo compartido del teclado.

## Ver el plan sin cambiar nada

```bash
bash install.sh --dry-run
bash install.sh hotkeys --dry-run
bash install.sh --help
```

`--dry-run` no instala paquetes, no cambia archivos y no reinicia servicios. Tampoco valida que se disponga de sudo o acceso al hardware.

## Actualizar

Descarga la nueva versión y vuelve a ejecutar `bash install.sh`. Las dependencias presentes se omiten; los programas y servicios se actualizan, los atajos propios se registran con sus valores actuales y los servicios se reinician. No es necesario reiniciar el equipo, aunque puede producirse un breve cambio de pantallas/teclado durante la actualización.

`install-hotkeys.sh` se conserva por compatibilidad: llama a la instalación completa. Para instalar solamente el servicio de teclas usa `install.sh hotkeys`.

## Verificar

```bash
systemctl is-enabled zenbook-duo-hotkeys.service
systemctl is-active zenbook-duo-hotkeys.service
systemctl --user is-enabled zenbook-duo-screen-toggle.service
systemctl --user is-active zenbook-duo-screen-toggle.service
```

Prueba acoplar y retirar el teclado, conectar y retirar pantallas externas, volumen, brillo y micrófono. Con ambas pantallas encendidas y teclado separado, prueba F8; F11 abre Caracteres y F12 abre Configuración.

Registros:

```bash
journalctl -u zenbook-duo-hotkeys.service -n 50 --no-pager
journalctl --user -u zenbook-duo-screen-toggle.service -n 50 --no-pager
```

Consulta [CONFIGURATION.md](CONFIGURATION.md) y [HOTKEYS.md](HOTKEYS.md) para los detalles y las limitaciones, incluida la iluminación del teclado por Bluetooth no implementada.

## Desinstalar por separado

### Hotkeys del sistema

```bash
sudo systemctl disable --now zenbook-duo-hotkeys.service
sudo rm -f /etc/systemd/system/zenbook-duo-hotkeys.service
sudo rm -f /usr/local/lib/zenbook-duo-hotkeys/duo-hotkeys.py
sudo rm -f /etc/modules-load.d/zenbook-duo-uinput.conf
sudo systemctl daemon-reload
```

No se descarga `uinput` del kernel porque otras aplicaciones pueden utilizarlo. Las copias `.before-FECHA` se conservan.

### Atajos

En **Configuración → Teclado → Atajos personalizados**, elimina `duo-toggle`, `duo-swap`, `duo-settings` y `duo-emoji`. No elimines otros atajos.

### Pantallas

```bash
bash uninstall.sh
```

Este desinstalador retira solo el servicio y el programa de pantallas; no elimina las hotkeys del sistema ni los atajos. Si la inferior permanece apagada, actívala en Configuración → Pantallas.

Para retirar todo, completa los tres apartados anteriores. Las dependencias compartidas y las copias de seguridad se conservan. Si deseas volver a la instalación anterior y todavía existe:

```bash
systemctl --user enable --now zenbook-duo.service
```
