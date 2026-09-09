#!/bin/bash
# Set up a user logrotate as the running user
mkdir -p ~/.config/logrotate.d

# Systemd it
cat << EOF > ~/.config/systemd/user/kaithem-tweaks-logrotate.service
[Unit]
Description=logrotate service for user $(id -un)
After=local-fs.target
Before=local-fs.target

[Service]
TimeoutStartSec=0
ExecStart=/bin/sh -c '/usr/sbin/logrotate -v -f -l /dev/null -s /dev/null %h/.config/logrotate.d/*'
Restart=on-failure
RestartSec=3600d
Type=simple

[Install]
WantedBy=default.target
EOF

# add timer

cat << EOF > ~/.config/systemd/user/kaithem-tweaks-logrotate.timer
[Unit]
Description=logrotate timer for user $(id -un)
After=local-fs.target
Before=local-fs.target

[Timer]
Unit=kaithem-tweaks-logrotate.service
Persistent=false
OnCalendar=*-*-* 03:00:00

[Install]
WantedBy=timers.target
EOF


cat << EOF > ~/.config/logrotate.d/kaithem-tweaks.conf
/home/$(id -un)/.cache/lxsession/LXDE-pi/run.log {
  rotate 2 
  daily
  compress
  missingok
  notifempty
}
EOF

systemctl --user enable kaithem-tweaks-logrotate.service
systemctl --user enable kaithem-tweaks-logrotate.timer
