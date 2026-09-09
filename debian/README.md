## KaithemAutomation Provisioning on Debian 

Run this as the kaithem user.  Some commands may use sudo
and ask for a password.

```bash
## Download this repo 
sudo apt install -y make git
git clone https://github.com/EternityForest/kaithem-scripts
cd kaithem-scripts/debian


## Use the script

make root-install-system-dependencies
make user-install-kaithem


## Give the kaithem user hardware permissions
#####################################################################3
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

```

## Configure the system

Use these commands to configure the system as desired.

For long term installation, root-install-sd-protection is probably a good idea.

These are meant to be used on a fresh Linux install and don't have uninstallers, use with care.


```bash
# Launch at startup
make user-start-kaithem-at-boot


# Some distros don't have pipewire JACK enabled by default, which
# is needed for the audio mixing features.
# Hopefully this is not needed on modern systems.
make root-use-pipewire-jack
make user-restart-pipewire


# This activates a maxvolume service, which sets volume to full at boot.
make user-max-volume-at-boot


# Linux by default has a LOT of stuff that writes
# excessively to the SD card. On a raspberry pi this
# Should make the system much more reliable without
# making anything work differently, except for putting logs in RAM
# Actually just run as user
make root-install-sd-protection


# Sets up a collection of misc tweaks that are recommended for kaithem.
make root-install-raspios-linux-tweaks


# Installs Mosquitto and sets it up to allow anonymous clients.
make root-enable-anon-mqtt


# Installs Mosquitto and sets it up to allow anonymous clients.
make root-uninstall-bloatware


# Set up the Pi to display the Kaithem homepage(Can configure redirect in settings)
# On boot in a fullscreen kiosk, under the default user.
# Tested on raspberry pi OS, may work on other lightdm systems.

# There's no automated uninstaller
make root-install-lightdm-kiosk

# Sets sudo to passwordless by creating a /etc/sudoers.d/sudo-nopasswd file
make root-enable-passwordless-sudo

```



## Matter Support

Kaithem has experimental support for the Matter protocol, if the python matter server is running.  Use this command to set it up with Docker:

```bash
kaithem-scripts root-setup-matter-server
```

Then add a MatterControllerClient device via the UI.  All commisioned devices will be auto-added as subdevices.