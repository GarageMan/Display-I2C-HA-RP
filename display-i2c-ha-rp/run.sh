#!/usr/bin/with-contenv bashio

echo "--- I2C Diagnose ---"
i2cdetect -y 1 || echo "Bus nicht erreichbar"

echo "--- Starte App ---"
python3 /app/display.py
