# Kaithem Docker install

Run as normal user. This script should work on Debian-like hosts(pi,ubuntu, etc).

For anything else, replace the apt-get commands with your equivalent.

```bash

# Download this repo.
sudo apt install -y make git
git clone https://github.com/EternityForest/kaithem-scripts
cd kaithem-scripts/docker


## Add needed user permissions

# The user kaithem runs as needs docker to launch the app
! sudo -E usermod -a -G docker $(id -un)

! sudo -E usermod -a -G audio $(id -un)
# Low latency audio
! sudo -E usermod -a -G rtkit $(id -un)
# serial ports and dmx adapters
! sudo -E usermod -a -G dialout $(id -un)
! sudo -E usermod -a -G serial $(id -un)

# USB hardware
! sudo -E usermod -a -G plugdev $(id -un)
# View system logs, used for kaithem's system error alerts
! sudo -E usermod -a -G adm $(id -un)
! sudo -E usermod -a -G bluetooth $(id -un)




# Install Docker however you prefer
sudo apt install git docker.io docker-compose-v2 docker-cli

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh


# OPTIONAL Enable system watchdog, prevent wifi sleep, other small tweaks
sudo bash ../debian/scripts/linux-tweaks.sh

# OPTIONAL Try to reduce SD card wear with some tmpfses and other tweaks.
# This needs to know what user to install things for, even though it is root
# level.
SD_PROTECT_UID=$(id -u) sudo -E ../debian/scripts/linux-sd-protect.sh

# Further reduce SD wear with some more commands that need to run as
# the user.
../debian/scripts/linux-sd-protect-user.sh

# This will install kaithem-host-services, which runs
# under systemd.  It can run as a normal user since we have added Docker.
bash install.sh

# Set up the OS to launch the "kiosk" service at boot with no
# screen saver
# Should work on debian-like OSes.
# There is no undo for this except by manually resetting the settings.


bash install-kiosk.sh


#########################################################################
# Tweak the docker-compose in kaithem-docker-home to 
# Change where this kiosk actually points.
# You will need to rerun the enable command to make it take effect
#########################################################################



# Actually launch. May take a while for first run
# as it must pull the dockers.
# Docker will automatically make this run at boot.
# To stop it, use the normal docker tools.

bash enable.sh

```

