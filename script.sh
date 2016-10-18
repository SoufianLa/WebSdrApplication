#!/bin/bash
cd Projet/Surveillance/
python server-surveillance.py &
while true
do
    python script_alarms.py
    echo "script 2 is executing .."
    sleep 2
done
