# Kaithem Docker install

Run as normal user. This script should work on Debian-like hosts(pi,ubuntu, etc).

For anything else, replace the apt-get commands with your equivalent.

```bash

# Download this repo.
sudo apt install -y make git
git clone https://github.com/EternityForest/kaithem-scripts
cd kaithem-scripts/debian



# Install Docker however you prefer
sudo apt install git docker.io docker-compose-v2 docker-cli

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh


# OPTIONAL Enable system watchdog, prevent wifi sleep, other small tweaks
sudo bash ../debian/scripts/linux-tweaks.sh

# OPTIONAL Enable system watchdog, prevent wifi sleep, other small tweaks
KAITHEM_USER=$(id -un) sudo -E sudo ../debian/scripts/linux-sd-protect.sh

# This will install kaithem-host-services, which runs
# under systemd
bash install.sh

# Set up the OS to launch the "kiosk" service at boot with no
# screen saver
# Should work on debian-like OSes.
# There is no undo for this except by manually resetting the settings.
# Tweak the docker-compose in kaithem-docker-home to 
# Change where this kiosk actually points.
bash install-kiosk.sh



# Actually launch. May take a while for first run
# as it must pull the dockers.
# Docker will automatically make this run at boot.
# To stop it, use the normal docker tools.

bash enable.sh

```

