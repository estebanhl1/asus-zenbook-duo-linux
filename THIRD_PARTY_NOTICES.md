# Código de terceros y créditos

## zenbook-duo-2024-ux8406ma-linux

- **Autora y titular del copyright:** Alesya Huzik ([@alesya-h](https://github.com/alesya-h)).
- **Repositorio original:** https://github.com/alesya-h/zenbook-duo-2024-ux8406ma-linux
- **Versión incluida:** commit `552050583f765da68ef1ad00d9d6a855b573dfcc`.
- **Enlace a esa versión:** https://github.com/alesya-h/zenbook-duo-2024-ux8406ma-linux/tree/552050583f765da68ef1ad00d9d6a855b573dfcc
- **Licencia del repositorio original:** BSD 2-Clause; se conserva íntegra en [LICENSE](third_party/zenbook-duo-2024-ux8406ma-linux/LICENSE).
- **Ubicación:** [third_party/zenbook-duo-2024-ux8406ma-linux](third_party/zenbook-duo-2024-ux8406ma-linux/).

Se incluye una copia de todos los archivos versionados del commit que estaba descargado en el equipo, sin modificaciones. No se incluyen su historial Git, las modificaciones locales ni datos del equipo. Los avisos y archivos originales se conservan tal como fueron publicados, incluidos los perfiles ICC; estos no son obra de este proyecto.

El proyecto original ofrece utilidades para pantallas, brillo, batería, rotación y teclado del ASUS Zenbook Duo. Su detección del teclado USB `0b05:1b2c` sirvió de referencia para el nuevo observador Python. Alesya Huzik recibe crédito por ese trabajo original; no se le atribuyen nuestras modificaciones ni se implica su respaldo a este proyecto.

El observador `duo-display-watch.py`, el servicio `zenbook-duo-screen-toggle.service`, los instaladores y las pruebas de la raíz se añadieron durante esta corrección. Los archivos nuevos se distribuyen bajo la licencia MIT de la raíz. La copia original conserva su licencia BSD 2-Clause; la licencia MIT de la raíz no sustituye los avisos ni las licencias de terceros.

## Uso de la copia original

El instalador de la raíz instala únicamente el nuevo observador. La copia original se incluye para conservar la base del trabajo y facilitar su consulta, y tiene sus propias dependencias e instrucciones en su [README](third_party/zenbook-duo-2024-ux8406ma-linux/README.md).

No ejecutes ambos observadores de pantallas al mismo tiempo. El nuevo observador no necesita los cambios de sudoers descritos en el README original.

## Referencia del protocolo USB de hotkeys

La herramienta experimental `tools/probe-usb-hotkeys.py` utiliza los comandos y códigos de protocolo documentados en `src/keyboard_usb.rs` de [PegasisForever/zenbook-duo-daemon](https://github.com/PegasisForever/zenbook-duo-daemon), commit `7955be868aba807b02ec748c02ab537aabec3ada`. Crédito a PegasisForever y los colaboradores del proyecto por ese trabajo. Se conserva su [licencia MIT original](third_party/zenbook-duo-daemon/LICENSE), literalmente como figura en el repositorio, incluidos sus campos sin completar. Esta carpeta solo contiene la licencia; no instala ese daemon.

La herramienta activa temporalmente el modo hotkeys por USB, muestra los códigos especiales durante 40 segundos y solicita el modo F al terminar. Todavía requiere validación en el equipo y no habilita el soporte completo de hotkeys en el servicio.

El nuevo `duo-hotkeys.py` también utiliza el protocolo USB y los códigos de esa referencia de PegasisForever. Sus detalles y estado de validación están en `HOTKEYS.md`.

La ampliación Bluetooth usa la correspondencia de ABS_MISC descrita en `src/keyboard_bt.rs` del mismo commit de PegasisForever; conserva el mismo crédito y licencia de referencia.
