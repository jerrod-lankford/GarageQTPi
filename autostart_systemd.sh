#!/bin/bash
cp garageqtpi@pi.service /etc/systemd/system/garageqtpi@${SUDO_USER:-${USER}}.service
sed -i "s?/home/pi/GarageQTPi?`pwd`?" /etc/systemd/system/garageqtpi@${SUDO_USER:-${USER}}.service
systemctl --system daemon-reload
systemctl enable garageqtpi@${SUDO_USER:-${USER}}.service
