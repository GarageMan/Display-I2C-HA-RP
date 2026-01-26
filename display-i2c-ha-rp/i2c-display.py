from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import time
import requests
import os
import logging
import socket
import sys
import datetime

# --- LOGGING ---
logging.basicConfig(level=logging.WARNING)

# --- INITIALISIERUNG ---
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    d = int(uptime_seconds // (24 * 3600))
    h = int((uptime_seconds % (24 * 3600)) // 3600)
    m = int((uptime_seconds % 3600) // 60)
    if d > 0:
        return f"{d}d {h}h {m}m"
    return f"{h}h {m}m"

def get_ha_info():
    token = os.getenv("SUPERVISOR_TOKEN") or os.getenv("HASSIO_TOKEN")
    try:
        url = "http://supervisor/info"
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(url, headers=headers, timeout=2)
        data = r.json().get("data", {})
        return data.get("state", "unknown"), data.get("version", "unknown")
    except:
        return "error", "unknown"

def get_disk_info():
    usage = psutil.disk_usage('/')
    free_gb = usage.free / (1024**3)
    return f"{usage.percent}%", f"{free_gb:.1f}GB"

def get_net_info():
    net = psutil.net_io_counters()
    # Umrechnung in MB
    mb_in = net.bytes_recv / (1024**2)
    mb_out = net.bytes_sent / (1024**2)
    return f"{mb_in:.0f}M", f"{mb_out:.0f}M"

# Display Setup
try:
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, width=128, height=64)
except Exception as e:
    sys.exit(1)

# Schriftarten (Standard)
font = ImageFont.load_default()

# Variablen
blink_state = False
last_blink = 0
last_update = 0
ip_addr = get_ip()
ha_version = "unknown"

# --- LOOP ---
while True:
    now = time.time()
    
    # 1. Page-Switch Logik (alle 5 Sekunden wechseln)
    # page 0: System / page 1: Storage & Net
    current_page = (int(now) // 5) % 2

    # 2. Blink-Frequenz (2Hz / 5Hz)
    ha_status, ha_version = get_ha_info()
    interval = 0.1 if ha_status != "running" else 0.25
    if now - last_blink >= interval:
        blink_state = not blink_state
        last_blink = now

    # 3. Daten-Update (alle 2 Sekunden)
    if now - last_update >= 2.0:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        temp = 0.0
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp = int(f.read()) / 1000.0
        except: pass
        uptime = get_uptime()
        disk_p, disk_f = get_disk_info()
        net_i, net_o = get_net_info()
        zeit = datetime.datetime.now().strftime("%H:%M:%S")
        last_update = now

    # --- ZEICHNEN ---
    img = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(img)

    # Zeile 1: IP-Header (Immer sichtbar)
    draw.text((0, 1), f"IP: {ip_addr}", font=font, fill=255)
    draw.line((0, 14, 128, 14), fill=255)
    
    # Inhaltsbereich (Wechselt je nach Seite)
    if current_page == 0:
        # SEITE 1: System Daten
        draw.text((0, 16),  f"CPU:  {cpu:>5.1f}%", font=font, fill=255)
        draw.text((0, 28),  f"RAM:  {ram:>5.1f}%", font=font, fill=255)
        draw.text((0, 40),  f"TEMP: {temp:>5.1f}C", font=font, fill=255)
    else:
        # SEITE 2: Disk, Net, Zeit
        draw.text((0, 16),  f"Disk: {disk_p} / {disk_f}", font=font, fill=255)
        draw.text((0, 28),  f"Net:  I:{net_i} O:{net_o}", font=font, fill=255)
        draw.text((0, 40),  f"Time: {zeit} | V:{ha_version[:5]}", font=font, fill=255)
    
    # Zeile 5: Footer (Immer sichtbar)
    draw.line((0, 52, 128, 52), fill=255)
    draw.text((0, 54), f"UP: {uptime}", font=font, fill=255)

    # Status LED (unten rechts)
    if blink_state:
        draw.ellipse((118, 54, 124, 60), outline=255, fill=255)
    else:
        draw.ellipse((118, 54, 124, 60), outline=255, fill=0)

    device.display(img)
    time.sleep(0.1)
