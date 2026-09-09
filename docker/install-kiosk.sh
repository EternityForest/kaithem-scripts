#!/bin/bash

#        _           _    
#   /\ /(_) ___  ___| | __
#  / //_/ |/ _ \/ __| |/ /
# / __ \| | (_) \__ \   < 
# \/  \/|_|\___/|___/_|\_\
                        

## Kaithem's opinionated way to do signage through the web

###############################################################################################################################

set -x
set -e

# Require root
if [ "$(id -u)" -eq 0 ]; then
        echo 'This script must not be run by root' >&2
        exit 1
fi


if command -v gsettings &> /dev/null; then
    echo "Ensuring screen saver is off"
    ! dbus-launch gsettings set org.gnome.desktop.screensaver lock-delay 3600
    ! dbus-launch gsettings set org.gnome.desktop.screensaver lock-enabled false
    ! dbus-launch gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
fi

# Needed to undo screen saver on pi
if command -v raspi-config &> /dev/null; then
  sudo raspi-config nonint do_blanking 1
fi

# TODO autologon on non-lightdm systems.
mkdir -p /etc/lightdm

SESSION_CFG=""


if [ -f /etc/lightdm/lightdm.conf ]; then
    sudo cp /etc/lightdm/lightdm.conf /etc/lightdm/lightdm.conf.backup-before-kiosk-mode
    sudo -E sed /etc/lightdm/lightdm.conf -i -e "s/^\(#\|\)autologin-user=.*/autologin-user=$(id -un)/"
fi

if [ -f /etc/gdm3/gdm.conf ]; then
    sudo cp /etc/gdm3/gdm.conf /etc/gdm3/gdm.conf.backup-before-kiosk-mode
    sudo -E sed /etc/gdm3/gdm.conf -i -e "s/^#  *AutomaticLogin *=.*/AutomaticLogin = $(id -un)/"
    sudo -E sed /etc/gdm3/gdm.conf -i -e "s/^#  *AutomaticLoginEnable *=.*/AutomaticLoginEnable = true/"

fi


# if rpi config exists
if command -v raspi-config &> /dev/null; then
  # Auto login
  echo "Configuring raspi to auto boot as default user"
  sudo raspi-config nonint do_boot_behaviour B4
fi

# Remove SSH warning on the pi.  Redundantly done in linux tweaks.
if [ -f /etc/profile.d/sshpwd.sh ]; then
    echo "Removing sshpwd.sh password change reminder"
    sudo rm -rf /etc/profile.d/sshpwd.sh
fi

if [ -f /etc/xdg/lxsession/LXDE-pi/sshpwd.sh ]; then
    echo "Removing sshpwd.sh password change reminder"
    sudo rm -rf /etc/xdg/lxsession/LXDE-pi/sshpwd.sh
fi

if [ -f /etc/xdg/autostart/pprompt.desktop ]; then
    echo "Removing pprompt.desktop password change reminder"
    sudo rm -rf /etc/xdg/autostart/pprompt.desktop
fi



mkdir -p $HOME/.config/autostart/

cat << EOF > $HOME/.config/autostart/kiosk.desktop
[Desktop Entry]
Name=EmberDefaultKiosk
Type=Application
Exec=sh -c "cd $HOME/kaithem-docker-home && KAITHEM_UID=$(id -u) KAITHEM_GROUP=$(id -g) KAITHEM_USER=$(id -un) docker compose up -f -d kiosk"
Terminal=false
EOF
