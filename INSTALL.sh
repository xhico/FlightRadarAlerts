#!/bin/bash

python3 -m pip install -r /home/pi/FlightRadarAlerts/requirements.txt --no-cache-dir
sudo mv /home/pi/FlightRadarAlerts/FlightRadarAlerts.service /etc/systemd/system/ && sudo systemctl daemon-reload
chmod +x -R /home/pi/FlightRadarAlerts/*