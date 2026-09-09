#!/bin/sh

# Install the host services app

echo "Installing kaithem-container-host-services"
sh ./kaithem-container-host-services/install.sh

mkdir -p ~/kaithem-docker-home

#If file doesn't exist, create it
if [ ! -f "~/kaithem-docker-home/docker-compose.yml" ]; then
    cp ./docker-compose.yml ~/kaithem-docker-home
else
    echo "~/kaithem-docker-home/docker-compose.yml already exists"
fi


cd ~/kaithem-docker-home

echo "Starting service"
KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) sudo -E docker compose up -d kaithem
