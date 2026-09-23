#!/usr/bin/env bash
set -euo pipefail
if [[ ${EUID} -eq 0 ]]; then
  echo 'Ejecuta este desinstalador como tu usuario, sin sudo.' >&2
  exit 1
fi
systemctl --user disable --now zenbook-duo-screen-toggle.service
rm -f -- "$HOME/.config/systemd/user/zenbook-duo-screen-toggle.service"
rm -f -- "$HOME/.local/share/zenbook-duo-screen-toggle/duo-display-watch.py"
rmdir -- "$HOME/.local/share/zenbook-duo-screen-toggle" 2>/dev/null || true
systemctl --user daemon-reload
echo 'Desinstalado. Si la pantalla inferior sigue apagada, actívala en Configuración → Pantallas.'
