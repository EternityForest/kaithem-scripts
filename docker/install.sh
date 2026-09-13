#!/bin/sh

# Install the host services app

echo "Installing kaithem-container-host-services"
bash ./kaithem-container-host-services/install.sh

# Very important not to let docker make these
# as root!!
mkdir -p ~/kaithem-docker-home
mkdir -p ~/kaithem-docker-home/kaithem
mkdir -p ~/kaithem-docker-home/matter


#If file doesn't exist, create it
if [ ! -f $HOME/kaithem-docker-home/docker-compose.yml ]; then
    cp ./docker-compose.yml ~/kaithem-docker-home
else
    echo "$HOME/kaithem-docker-home/docker-compose.yml already exists"
fi

bash ./compose-groups-override.sh

cd $HOME/kaithem-docker-home

echo "Starting service"
KAITHEM_GROUPS=$(getent group audio video dialout rtkit gpio i2c spi render bluetooth serial | cut -d: -f3 | tr '\n' ' ') KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) sudo -E docker compose up --remove-orphans -d kaithem matter
