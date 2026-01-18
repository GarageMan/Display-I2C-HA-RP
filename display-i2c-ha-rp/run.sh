#!/bin/bash
echo "--- Kaltstart ohne s6-overlay ---"
i2cdetect -y 1 || echo "Bus nicht erreichbar"

echo "--- Starte Python ---"
cd /app
python3 display.py
