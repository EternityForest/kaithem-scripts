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

echo "Ensuring $(id -un) is in permission groups"

# Need docker to launch the app
! sudo -E usermod -a -G docker $(id -un)

! sudo -E usermod -a -G audio $(id -un)
# Low latency audio
! sudo -E usermod -a -G rtkit $(id -un)
# serial ports and dmx adapters
! sudo -E usermod -a -G dialout $(id -un)
! sudo -E usermod -a -G serial $(id -un)

# USB hardware
! sudo -E usermod -a -G plugdev $(id -un)
# View system logs
! sudo -E usermod -a -G adm $(id -un)
! sudo -E usermod -a -G bluetooth $(id -un)


cd ~/kaithem-docker-home

echo "Starting service"
docker compose up -d kaithem

open http://localhost:8002