#!/usr/bin/env bash

echo "--- START OHNE S6 WRAPPER ---"
i2cdetect -y 1 || echo "Bus-Scan fehlgeschlagen"

echo "--- Starte Python App ---"
cd /app
python3 display.py
