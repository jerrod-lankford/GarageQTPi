#!/bin/bash
cp garageqtpi@pi.service /etc/systemd/system/garageqtpi@`whoami`.service
sed -i "s?/home/pi/GarageQTPi?`pwd`?" /etc/systemd/system/garageqtpi@`whoami`.service
systemctl --system daemon-reload
systemctl enable home-assistant@`whoami`
