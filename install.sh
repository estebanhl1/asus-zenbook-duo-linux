#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
component=all
non_interactive=0
dry_run=0
usage() {
  cat <<'HELP'
Uso: ./install.sh [all|displays|hotkeys|shortcuts|dependencies] [--non-interactive] [--dry-run]
  all            Instala todo (opción predeterminada).
  displays       Control automático de pantallas y sus dependencias.
  hotkeys        Servicio USB/Bluetooth y sus dependencias; sin atajos GNOME.
  shortcuts      Atajos GNOME; requiere instalar displays previamente.
  dependencies   Solo dependencias del conjunto completo.
  --non-interactive  Nunca pregunta: sudo -n; falla si no está autorizado.
  --dry-run      Muestra el plan; no instala ni modifica nada.
Ejecutar como usuario normal dentro de una sesión GNOME en Fedora.
HELP
}
chosen=0
for arg in "$@"; do
  case "$arg" in
    all|displays|hotkeys|shortcuts|dependencies)
      if (( chosen )); then echo 'Elige un solo componente.' >&2; exit 2; fi
      component=$arg; chosen=1 ;;
    --non-interactive) non_interactive=1 ;;
    --dry-run) dry_run=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opción desconocida: $arg" >&2; usage >&2; exit 2 ;;
  esac
done
packages=(python3 python3-gobject)
case "$component" in
  all|dependencies) packages+=(python3-pyusb python3-evdev gnome-characters gnome-control-center) ;;
  hotkeys) packages=(python3 python3-pyusb python3-evdev) ;;
  shortcuts) packages+=(gnome-characters gnome-control-center) ;;
esac
if (( dry_run )); then
  echo "Componente: $component"
  echo "Dependencias Fedora: ${packages[*]}"
  echo 'Los paquetes ya instalados se omiten. Las versiones locales reemplazadas tendrán copia .before-FECHA.'
  [[ $component == all || $component == displays ]] && echo 'Instalar servicio de pantallas de usuario; desactivar zenbook-duo.service antiguo.'
  [[ $component == all || $component == hotkeys ]] && echo 'Instalar servicio de hotkeys del sistema; cargar y configurar uinput al arrancar.'
  [[ $component == all || $component == shortcuts ]] && echo 'Guardar los cuatro atajos GNOME y conservar los demás.'
  echo "Modo sin preguntas: $non_interactive"
  exit 0
fi
if (( EUID == 0 )); then
  echo 'Ejecuta ./install.sh sin sudo para configurar la sesión del usuario correcto.' >&2; exit 1
fi
. /etc/os-release
[[ ${ID:-} == fedora ]] || { echo 'Este instalador automático admite Fedora. Consulta INSTALL.md.' >&2; exit 1; }
if [[ $component == all || $component == displays || $component == shortcuts ]]; then
  [[ ${XDG_CURRENT_DESKTOP:-} == *GNOME* ]] || { echo 'Ejecuta desde una sesión gráfica GNOME.' >&2; exit 1; }
  systemctl --user show-environment >/dev/null
fi
app_dir="$HOME/.local/share/zenbook-duo-screen-toggle"
unit_dir="$HOME/.config/systemd/user"
if [[ $component == shortcuts && ! -f $app_dir/duo-display-watch.py ]]; then
  echo 'Instala primero ./install.sh displays; estos atajos necesitan su programa.' >&2; exit 1
fi
priv=(sudo)
(( non_interactive )) && priv+=(-n)
missing=()
for package in "${packages[@]}"; do
  rpm -q "$package" >/dev/null 2>&1 || missing+=("$package")
done
if (( ${#missing[@]} )) || [[ $component == all || $component == hotkeys ]]; then
  "${priv[@]}" -v
fi
if (( ${#missing[@]} )); then
  "${priv[@]}" dnf -y install "${missing[@]}"
fi
stamp=$(date +%Y%m%d-%H%M%S)-$$
copy_user() {
  local source=$1 target=$2
  if [[ -f $target ]] && ! cmp -s "$source" "$target"; then cp -p -- "$target" "$target.before-$stamp"; fi
  install -m 644 -- "$source" "$target"
}
copy_system() {
  local source=$1 target=$2
  if [[ -f $target ]] && ! cmp -s "$source" "$target"; then "${priv[@]}" cp -p -- "$target" "$target.before-$stamp"; fi
  "${priv[@]}" install -m 644 -- "$source" "$target"
}
if [[ $component == all || $component == displays ]]; then
  /usr/bin/python3 -c 'from gi.repository import Gio, GLib'
  mkdir -p -- "$app_dir" "$unit_dir"
  copy_user duo-display-watch.py "$app_dir/duo-display-watch.py"
  copy_user zenbook-duo-screen-toggle.service "$unit_dir/zenbook-duo-screen-toggle.service"
  if systemctl --user cat zenbook-duo.service >/dev/null 2>&1; then
    systemctl --user disable --now zenbook-duo.service
  fi
  systemctl --user daemon-reload
  systemctl --user enable zenbook-duo-screen-toggle.service
  systemctl --user restart zenbook-duo-screen-toggle.service
  systemctl --user is-active --quiet zenbook-duo-screen-toggle.service
fi
if [[ $component == all || $component == shortcuts ]]; then
  mkdir -p -- "$app_dir"
  dconf dump /org/gnome/settings-daemon/plugins/media-keys/ > "$app_dir/shortcuts.before-$stamp.dconf"
  /usr/bin/python3 setup-hotkey-shortcuts.py
fi
if [[ $component == all || $component == hotkeys ]]; then
  /usr/bin/python3 -c 'import usb.core, evdev'
  "${priv[@]}" install -d -m 755 /usr/local/lib/zenbook-duo-hotkeys /etc/modules-load.d
  copy_system duo-hotkeys.py /usr/local/lib/zenbook-duo-hotkeys/duo-hotkeys.py
  copy_system zenbook-duo-hotkeys.service /etc/systemd/system/zenbook-duo-hotkeys.service
  copy_system zenbook-duo-uinput.conf /etc/modules-load.d/zenbook-duo-uinput.conf
  "${priv[@]}" modprobe uinput
  "${priv[@]}" systemctl daemon-reload
  "${priv[@]}" systemctl enable zenbook-duo-hotkeys.service
  "${priv[@]}" systemctl restart zenbook-duo-hotkeys.service
  "${priv[@]}" systemctl is-active --quiet zenbook-duo-hotkeys.service
fi
echo "Instalación terminada: $component."
