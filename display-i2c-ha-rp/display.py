from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import time
import requests
import os
import logging
import sys

# Logging nur für Warnungen und Fehler
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def init_display(retries=5, delay=2):
    for i in range(retries):
        try:
            serial = i2c(port=1, address=0x3C)
            device = ssd1306(serial, width=128, height=64)
            return device
        except Exception as e:
            # Fehler werden weiterhin geloggt
            logging.error(f"Display Fehler: {e}")
            time.sleep(delay)
    return None

device = init_display()
if not device:
    sys.exit(1)

font_small = ImageFont.load_default()
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN") or os.getenv("HASSIO_TOKEN")
SUPERVISOR_URL = "http://supervisor/info"

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000.0
    except:
        return 0.0

def get_ha_status():
    if not SUPERVISOR_TOKEN: return "no_auth"
    try:
        headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
        r = requests.get(SUPERVISOR_URL, headers=headers, timeout=2)
        return r.json().get("data", {}).get("state", "unknown")
    except:
        return "error"

blink_state = False
last_blink = time.time()
last_update = 0
cpu = ram = temp = 0.0
ha_status = "?"

while True:
    try:
        now = time.time()
        
        # Blink-Frequenz Logik
        blink_interval = 0.1 if ha_status != "running" else 0.25
        if now - last_blink >= blink_interval:
            blink_state = not blink_state
            last_blink = now

        # Daten-Update (OHNE logging.info)
        if now - last_update >= 1.0:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            temp = get_cpu_temp()
            ha_status = get_ha_status()
            last_update = now

        # Bild erstellen
        img = Image.new("1", (128, 64), 0)
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), "System Monitor", font=font_small, fill=255)
        draw.text((0, 14), f"CPU: {cpu:4.1f}%", font=font_small, fill=255)
        draw.text((0, 26), f"RAM: {ram:4.1f}%", font=font_small, fill=255)
        draw.text((0, 38), f"Temp: {temp:4.1f}C", font=font_small, fill=255)
        draw.text((0, 50), f"HA: {ha_status}", font=font_small, fill=255)

        # Status LED
        fill = 255 if blink_state else 0
        draw.ellipse((116, 50, 124, 58), outline=255, fill=fill)

        device.display(img)
        
    except Exception as e:
        logging.error(f"Schleifenfehler: {e}")
        time.sleep(1)

    time.sleep(0.05)
