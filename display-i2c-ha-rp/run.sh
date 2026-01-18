#!/usr/bin/with-contenv bashio

echo "--- DEBUG: System-Check ---"
echo "Benutzer-ID: $(id)"
echo "Verfügbare I2C-Busse:"
ls -l /dev/i2c* || echo "Keine I2C-Devices in /dev gefunden!"

echo "--- DEBUG: I2C-Bus Diagnose ---"
# -y 1 scannt Bus 1. Wir nutzen auch 'i2cdump' falls vorhanden für tieferen Check.
if [ -e /dev/i2c-1 ]; then
    echo "Scan Bus 1..."
    i2cdetect -y 1 || echo "i2cdetect fehlgeschlagen - Berechtigungsproblem?"
else
    echo "FEHLER: /dev/i2c-1 existiert nicht. Ist I2C im Host aktiviert?"
fi

echo "--- Starte Python App ---"
cd /app
# Wir nutzen 'exec', damit Python die PID 1 von der Shell übernimmt
exec python3 display.py
