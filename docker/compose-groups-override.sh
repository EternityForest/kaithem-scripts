#!/usr/bin/env bash
# Generate docker/docker-compose.override.yaml with KAITHEM_GROUPS inlined as a
# real YAML list, so `group_add:` is a proper list (docker compose only does
# text substitution for env vars; it does not parse `[a,b,c]` as a list).
#
# Usage (standalone, outside Make):
#   scripts/render-compose-override.sh
#   COMPOSE_FILE=docker/docker-compose.yaml:docker/docker-compose.override.yaml \
#     docker compose up -d
#
# The list of groups is whatever `getent` finds on the host for these names:
# audio video dialout rtkit gpio i2c spi render bluetooth serial
# Missing groups are silently dropped; if none are found the list is [].
set -euo pipefail

cd "$(dirname "$0")"

# Resolve GIDs, space-separated, trimmed. Query each group individually so
# `getent`'s non-zero exit on missing groups does not poison the pipeline.
gids=""
for grp in audio video dialout rtkit gpio i2c spi render bluetooth serial; do
    if gid=$(getent group "$grp" | cut -d: -f3); then
        [ -n "$gid" ] && gids="${gids:+$gids }$gid"
    fi
done

# YAML flow sequence: ["29", "44", ...]; [] if empty.
list=$(printf '%s\n' $gids \
        | awk 'BEGIN{printf "["}
               {printf "%s\"%s\"", (NR>1?",":""), $1}
               END{print "]"}')

cat << EOF > $HOME/kaithem-docker-home/compose-groups.yml
name: kaithem
services:
  kaithem:
    group_add: ${list}
  kaithem-kiosk:
    group_add: ${list}
EOF
