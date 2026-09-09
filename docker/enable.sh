#!/bin/bash

cd ~/kaithem-docker-home
KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) docker compose up -d kaithem kiosk