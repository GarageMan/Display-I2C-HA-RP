from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import time
import requests
import os
import logging
import sys

# Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("Display-Skript startet...")

# --- INITIALISIERUNG MIT FEHLERBEHANDLUNG ---

def init_display(retries=5, delay=2):
    """Versucht das Display mehrmals zu initialisieren."""
    for i in range(retries):
        try:
            # I2C Display Initialisierung 
            serial = i2c(port=1, address=0x3C)
            device = ssd1306(serial, width=128, height=64)
            logging.info("Display erfolgreich initialisiert!")
            return device
        except Exception as e:
            logging.warning(f"Versuch {i+1}/{retries}: Display nicht gefunden ({e}). Warte {delay}s...")
            time.sleep(delay)
    return None

device = init_display()

if not device:
    logging.critical("Hardware-Verbindung fehlgeschlagen. Add-on wird beendet.")
    sys.exit(1)

# --- HELFERFUNKTIONEN ---

font_small = ImageFont.load_default()

# Token-Abfrage für verschiedene HA-Versionen 
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN") or os.getenv("HASSIO_TOKEN")
SUPERVISOR_URL = "http://supervisor/info"

def get_cpu_temp():
    try:
        # Standardpfad für Raspberry Pi Temperatur 
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000.0
    except Exception as e:
        logging.error(f"Fehler beim Lesen der CPU-Temperatur: {e}")
        return 0.0

def get_ha_status():
    if not SUPERVISOR_TOKEN:
        return "no_auth"
    try:
        headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
        r = requests.get(SUPERVISOR_URL, headers=headers, timeout=2)
        data = r.json()
        return data.get("data", {}).get("state", "unknown")
    except Exception as e:
        logging.error(f"Fehler beim Lesen des HA-Status: {e}")
        return "error"

# --- HAUPTSCHLEIFE ---

last_update = 0
update_interval = 1.0
cpu = ram = temp = 0.0
ha_status = "?"

while True:
    try:
        now = time.time()

        # Daten aktualisieren 
        if now - last_update >= update_interval:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            temp = get_cpu_temp()
            ha_status = get_ha_status()
            last_update = now
            logging.info(f"CPU={cpu:.1f}% RAM={ram:.1f}% Temp={temp:.1f}°C HA={ha_status}")

        # Bild erstellen 
        img = Image.new("1", (128, 64), 0)
        draw = ImageDraw.Draw(img)

        # UI Zeichnen 
        draw.text((0, 0), "System Monitor", font=font_small, fill=255)
        draw.text((0, 14), f"CPU: {cpu:4.1f}%", font=font_small, fill=255)
        draw.text((0, 26), f"RAM: {ram:4.1f}%", font=font_small, fill=255)
        draw.text((0, 38), f"Temp: {temp:4.1f}C", font=font_small, fill=255)
        draw.text((0, 50), f"HA: {ha_status}", font=font_small, fill=255)

        # Balken-Anzeige 
        bar_x, bar_width, bar_height = 70, 50, 6
        draw.rectangle((bar_x, 16, bar_x + bar_width, 16 + bar_height), outline=255)
        draw.rectangle((bar_x, 16, bar_x + int(bar_width * cpu / 100), 16 + bar_height), fill=255)
        draw.rectangle((bar_x, 28, bar_x + bar_width, 28 + bar_height), outline=255)
        draw.rectangle((bar_x, 28, bar_x + int(bar_width * ram / 100), 28 + bar_height), fill=255)

        # Status LED (Rechts unten) 
        fill = 255 if ha_status == "running" else 0
        draw.ellipse((116, 50, 124, 58), outline=255, fill=fill)

        # An Hardware senden
        device.display(img)
        
    except OSError as e:
        logging.error(f"I2C Kommunikationsfehler während des Betriebs: {e}")
        time.sleep(2)  # Kurze Pause zur Erholung des Busses
    except Exception as e:
        logging.error(f"Unerwarteter Fehler in der Schleife: {e}")
        time.sleep(1)

    time.sleep(0.1)
