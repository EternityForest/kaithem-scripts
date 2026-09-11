#!/bin/bash

cd ~/kaithem-docker-home
KAITHEM_GROUPS=$(getent group audio video dialout rtkit gpio i2c spi render bluetooth serial | cut -d: -f3 | tr '\n' ' ') KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) sudo -E docker compose up -d kaithem