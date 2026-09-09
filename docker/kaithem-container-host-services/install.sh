#!/usr/bin/env bash
# Install kaithem-host-services as a uv tool and register it as a systemd
# --user service that starts on login.
set -euo pipefail

echo ">> Installing kaithem-host-services"


# Allow `bash install.sh` even if the user forgot to chmod +x.
if [[ "${BASH_SOURCE[0]}" == "${0}" && ! -x "${BASH_SOURCE[0]}" ]]; then
    exec bash "$0" "$@"
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">> Installing kaithem-host-services as a uv tool from $HERE"
UV_LINK_MODE=copy uv tool install "$HERE"

UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$UNIT_DIR"
install -m 0644 "$HERE/systemd/kaithem-host-services.service" "$UNIT_DIR/kaithem-host-services.service"

echo ">> Reloading systemd --user"
systemctl --user daemon-reload
systemctl --user enable --now kaithem-host-services.service

echo ">> Status:"
systemctl --user --no-pager status kaithem-host-services.service || true

echo
echo "Socket path (on the host):"
"${HOME}/.local/bin/kaithem-host-services" print-socket-path || true
