# ASUS Zenbook Duo — apagado automático de la pantalla inferior

Un pequeño servicio para **Linux con GNOME y Wayland** que apaga la pantalla inferior al colocar el teclado del Zenbook Duo y la vuelve a encender al retirarlo. Funciona también cuando hay monitores externos conectados.

Es una automatización de usuario mediante la API de pantallas de Mutter; no modifica el driver ni el kernel y no necesita permisos de administrador para funcionar.

## Equipo probado

- ASUS Zenbook Duo **UX8406MA**.
- Fedora Workstation 44, GNOME/Wayland, kernel 7.1.3.
- Dos pantallas internas de 2880 × 1800 a 120 Hz y dos monitores externos.
- Escala fraccional en las pantallas internas.

Se verificó el apagado y la restauración conservando la distribución de pantallas. Otros modelos, distribuciones y configuraciones todavía no se han probado.

## Qué hace

- Detecta el teclado acoplado por su identificador USB `0b05:1b2c` en `/sys/bus/usb/devices`.
- Revisa el estado cada segundo y espera 0,4 segundos para filtrar cambios transitorios.
- Quita `eDP-2` de la configuración activa al acoplar el teclado.
- Guarda en memoria la configuración de la pantalla inferior para restaurarla al desacoplarlo. Si cambió la distribución de las demás pantallas, recalcula su posición debajo de la superior.
- Comprueba también el estado de las pantallas cada segundo para recuperarse de conexiones y desconexiones de monitores externos.
- Conserva los parámetros de los demás monitores al crear la nueva configuración.
- Pide a Mutter que valide la configuración antes de aplicarla temporalmente.
- Evita apagar la única pantalla activa o modificar una pantalla inferior en modo espejo.

## Teclas especiales

Hay un módulo de hotkeys experimental y un instalador independiente: consulta [HOTKEYS.md](HOTKEYS.md) para funciones, instalación y limitaciones. Incluye recepción de hotkeys por Bluetooth. El usuario confirmó el funcionamiento tras corregir F8/F11/F12 el 23 de septiembre de 2026.

La configuración completa reproducible está resumida en [CONFIGURATION.md](CONFIGURATION.md).

## Requisitos

- GNOME con Mutter y una sesión Wayland con systemd de usuario.
- Python 3 y PyGObject (`gi.repository.Gio` y `GLib`).
- Pantalla superior identificada como `eDP-1` e inferior como `eDP-2`.

En Fedora puedes instalar las dependencias con:

```bash
sudo dnf install python3 python3-gobject
```

Comprueba la importación:

```bash
/usr/bin/python3 -c 'from gi.repository import Gio, GLib'
```

## Instalación

Desde la carpeta del repositorio, en una terminal GNOME, ejecuta **sin sudo**:

```bash
bash install.sh
```

Instala automáticamente dependencias, control de pantallas, hotkeys USB/Bluetooth y atajos. Puede solicitar la contraseña de sudo; `--non-interactive` evita preguntas y exige autorización previa.

Para instalar por separado:

```bash
bash install.sh displays
bash install.sh hotkeys
bash install.sh shortcuts
```

Consulta [INSTALL.md](INSTALL.md) para instalación desatendida, componentes, actualización y desinstalación. El instalador completo deshabilita el antiguo `zenbook-duo.service` si existe y conserva sus archivos.

## Prueba

1. Retira el teclado y deja ambas pantallas internas encendidas.
2. Colócalo sobre la pantalla inferior: debería apagarse en aproximadamente dos segundos.
3. Retíralo: la pantalla inferior debería volver a encenderse.
4. Repite con monitores externos conectados.

Para validar la configuración de apagado sin aplicarla:

```bash
/usr/bin/python3 duo-display-watch.py --verify-docked
```

Estado y registros:

```bash
systemctl --user status zenbook-duo-screen-toggle.service
journalctl --user -u zenbook-duo-screen-toggle.service -n 50 --no-pager
```

## Limitaciones conocidas

- El identificador USB y los conectores están fijados para el modelo probado.
- No es compatible con KDE ni con otros gestores de pantalla.
- La posición guardada vive en memoria. Tras reiniciar el servicio con la pantalla inferior apagada, se intenta colocarla debajo de la superior con una escala compatible.
- Al cambiar la distribución externa, descarta la posición antigua de la pantalla inferior. En distribuciones especiales, el espacio debajo de la superior puede estar ocupado; Mutter valida el resultado y registra un error si no es válido.
- El servicio mantiene la pantalla inferior encendida sin el teclado acoplado y apagada con él. Para controlarla manualmente, detén primero el servicio.
- No modifica por separado la entrada táctil de la pantalla inferior.
- No gestiona la pantalla de inicio de sesión.

## Desinstalación

Para retirar todo, sigue [INSTALL.md](INSTALL.md#desinstalar-por-separado). `uninstall.sh` solo retira el control de pantallas.

```bash
./uninstall.sh
```

Si la pantalla inferior queda apagada, actívala en **Configuración → Pantallas**. Para volver al servicio anterior, si lo tenías instalado:

```bash
systemctl --user enable --now zenbook-duo.service
```

## Desarrollo

Las pruebas usan un estado simulado de Mutter y no cambian las pantallas:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
bash -n install.sh uninstall.sh
```

## Origen y créditos

Este trabajo parte de una instalación de **[zenbook-duo-2024-ux8406ma-linux](https://github.com/alesya-h/zenbook-duo-2024-ux8406ma-linux)**, creado por **[Alesya Huzik (@alesya-h)](https://github.com/alesya-h)**. Gracias a su trabajo original sobre el soporte Linux del Zenbook Duo y la detección del teclado acoplado.

Incluimos una copia sin modificaciones de la versión que estaba descargada, commit `552050583f765da68ef1ad00d9d6a855b573dfcc`, en [third_party/zenbook-duo-2024-ux8406ma-linux](third_party/zenbook-duo-2024-ux8406ma-linux/), con su **licencia BSD 2-Clause** y avisos originales. Contiene el programa `duo`, las utilidades auxiliares y los perfiles ICC originales.

Nuestra corrección añade el observador Python para gestionar la pantalla inferior con monitores externos conectados. El instalador de la raíz instala ese observador; la copia original se conserva aparte y no se ejecuta automáticamente.

Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para los créditos, procedencia y alcance de la licencia. Los archivos nuevos se distribuyen bajo la [licencia MIT](LICENSE). Los componentes de terceros conservan sus licencias y avisos originales.

## Publicarlo en GitHub

Crea un repositorio vacío en GitHub y, desde esta carpeta, ejecuta:

```bash
git add .
git commit -m "Add Zenbook Duo automatic lower display toggle"
git remote add origin https://github.com/TU_USUARIO/zenbook-duo-screen-toggle.git
git push -u origin main
```

La carpeta ya está inicializada como repositorio Git, sin commits ni remoto. El código nuevo se publica bajo MIT. El código original incluido conserva su licencia BSD 2-Clause y sus créditos.
