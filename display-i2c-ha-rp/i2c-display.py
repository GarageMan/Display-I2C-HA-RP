from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import time
import requests
import os
import logging
import sys

# RADIKALE LOGGING-SPERRE: 
# Wir setzen das Level auf ERROR. Damit werden WARNING und INFO komplett ignoriert.
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# --- FUNKTIONEN ---

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000.0
    except:
        return 0.0

def get_ha_status():
    token = os.getenv("SUPERVISOR_TOKEN") or os.getenv("HASSIO_TOKEN")
    if not token:
        return "Auth-Error"
    try:
        url = "http://supervisor/info"
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(url, headers=headers, timeout=2)
        return r.json().get("data", {}).get("state", "unknown")
    except:
        return "Verbindung..."

# --- INITIALISIERUNG ---

try:
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, width=128, height=64)
except Exception as e:
    # Nur im absoluten Notfall direkt auf die Konsole schreiben
    sys.stderr.write(f"Hardware-Fehler: {e}\n")
    sys.exit(1)

# --- SETUP ---

font = ImageFont.load_default()
blink_state = False
last_blink = time.time()
last_update = 0

cpu = ram = temp = 0.0
ha_status = "?"

# --- HAUPTSCHLEIFE ---

while True:
    try:
        now = time.time()

        # Blink-Logik (2 Hz bei OK, 5 Hz bei Fehler)
        interval = 0.1 if ha_status != "running" else 0.25
        if now - last_blink >= interval:
            blink_state = not blink_state
            last_blink = now

        # Daten-Update alle 1 Sekunde
        if now - last_update >= 1.0:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            temp = get_cpu_temp()
            ha_status = get_ha_status()
            last_update = now
            # HIER GIBT ES KEINE PRINT ODER LOGGING BEFEHLE MEHR!

        # Zeichnen
        img = Image.new("1", (128, 64), 0)
        draw = ImageDraw.Draw(img)

        # UI Texte
        draw.text((0, 0), "SYSTEM MONITOR", font=font, fill=255)
        draw.text((0, 14), f"CPU: {cpu:4.1f}%", font=font, fill=255)
        draw.text((0, 26), f"RAM: {ram:4.1f}%", font=font, fill=255)
        draw.text((0, 38), f"Temp: {temp:4.1f}C", font=font, fill=255)
        draw.text((0, 50), f"HA: {ha_status}", font=font, fill=255)

        # Balken
        bx, bw, bh = 70, 50, 6
        draw.rectangle((bx, 16, bx+bw, 16+bh), outline=255)
        draw.rectangle((bx, 16, bx+int(bw*cpu/100), 16+bh), fill=255)
        draw.rectangle((bx, 28, bx+bw, 28+bh), outline=255)
        draw.rectangle((bx, 28, bx+int(bw*ram/100), 28+bh), fill=255)

        # Status LED
        if blink_state:
            draw.ellipse((116, 50, 124, 58), outline=255, fill=255)
        else:
            draw.ellipse((116, 50, 124, 58), outline=255, fill=0)

        device.display(img)

    except Exception:
        # Im Fehlerfall einfach kurz warten und weitermachen
        time.sleep(1)

    time.sleep(0.05)
