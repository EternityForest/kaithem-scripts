#!/bin/sh

# Install the host services app

echo "Installing kaithem-container-host-services"
bash ./kaithem-container-host-services/install.sh

mkdir -p ~/kaithem-docker-home

#If file doesn't exist, create it
if [ ! -f $HOME/kaithem-docker-home/docker-compose.yml ]; then
    cp ./docker-compose.yml ~/kaithem-docker-home
else
    echo "$HOME/kaithem-docker-home/docker-compose.yml already exists"
fi


cd $HOME/kaithem-docker-home

echo "Starting service"
KAITHEM_GROUPS=$(getent group audio video dialout rtkit gpio i2c spi render bluetooth serial | cut -d: -f3 | tr '\n' ' ') KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) sudo -E docker compose up -d kaithem
