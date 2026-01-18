#!/bin/bash
# Kurze Statusmeldung beim Start
echo "[Status] Add-on Initialisierung..."

# I2C Scan nur ausführen, aber Ausgabe unterdrücken, wenn nicht nötig
# Oder einfach so lassen, da es nur einmal beim Start erscheint
i2cdetect -y 1

echo "[Status] Python-App wird gestartet..."
cd /app
exec python3 i2c-display.py
