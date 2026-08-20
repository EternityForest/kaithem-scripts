#!/usr/bin/env bash
# Uninstall kaithem-host-services: stop the systemd --user service and
# remove the uv tool install.
set -euo pipefail

if [[ "${BASH_SOURCE[0]}" == "${0}" && ! -x "${BASH_SOURCE[0]}" ]]; then
    exec bash "$0" "$@"
fi

UNIT="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/kaithem-host-services.service"

echo ">> Stopping and disabling systemd --user unit"
systemctl --user disable --now kaithem-host-services.service 2>/dev/null || true

if [[ -f "$UNIT" ]]; then
    rm -f "$UNIT"
    systemctl --user daemon-reload
fi

echo ">> Uninstalling uv tool"
uv tool uninstall kaithem-host-services || true
