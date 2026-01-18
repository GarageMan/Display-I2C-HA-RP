# I2C System Display für Home Assistant

Dieses Add-on zeigt CPU-Last, RAM-Verbrauch, Temperatur und den Home Assistant Status auf einem **SSD1306 OLED Display** (128x64) an.

- CPU-Auslastung
- RAM-Auslastung
- CPU-Temperatur
- Home Assistant Status mittels "Status-LED"

## 1. Hardware-Vorbereitung

Verbinde das Display mit den GPIO-Pins deines Raspberry Pi 4:

| Display Pin | Raspberry Pi Pin | Funktion |
| --- | --- | --- |
| VCC | Pin 1 | 3.3V Strom |
| GND | Pin 6 | Masse |
| SDA | Pin 3 (GPIO 2) | Datenleitung |
| SCL | Pin 5 (GPIO 3) | Taktleitung |

## 2. I2C am Host aktivieren (Wichtig!)

Home Assistant OS benötigt eine explizite Freigabe für den I2C-Bus auf der Hardware-Ebene:

1. SD-Karte am PC öffnen.
2. In der Partition `hassos-boot` die Datei `config.txt` suchen.
3. Folgende Zeilen am Ende hinzufügen:
```text
dtparam=i2c_arm=on
dtparam=i2c_vc=on
dtoverlay=i2c-rtc,ds3231
```

4. SD-Karte wieder in den Pi stecken und neu starten.

## 3. Installation des Add-ons

1. Gehe in Home Assistant zu **Einstellungen** > **Add-ons** > **Add-on Store**.
2. Klicke oben rechts auf die drei Punkte > **Repositories**.
3. Füge die URL deines GitHub-Repositories hinzu.
4. Suche das Add-on **"I2C System Display"** und klicke auf **Installieren**.

## 4. Konfiguration & Start

Bevor du das Add-on startest, sind zwei Sicherheitseinstellungen zwingend erforderlich:

1. Öffne die Seite des installierten Add-ons.
2. Deaktiviere den **"Gesicherten Modus"** (Protection Mode), damit das Add-on auf die GPIO-Pins zugreifen darf.
3. Aktiviere (optional) **"In der Seitenleiste anzeigen"**.
4. Klicke auf **Starten**.

## 5. Status-LED (Punkt unten rechts)

* **Blinkt langsam (2 Hz):** Home Assistant läuft korrekt (`running`).
* **Blinkt schnell (5 Hz):** Home Assistant startet noch oder es liegt ein Fehler vor.

## 6. Layout "The Tech-Header"

| Bereich | Inhalt | Design |
| --- | --- | --- |
| Oben (Invertiert) | 192.168.178.50 | "Weißer Balken, schwarzer Text (fett)" |
| Mitte Links | CPU: 12% / TEMP: 42°C | Icons oder fette Schrift |
| Mitte Rechts | RAM: 1.2/4GB | Textuell statt Balken |
| Unten | Uptime: 2d 14h | "Kleiner, dezenter Text" |
| Ecke unten rechts | Status-Punkt | Dein bewährtes Blinken |

<img width="240" height="177" alt="image" src="https://github.com/user-attachments/assets/c894e0d4-db1c-40bf-93ad-6c58d05b3788" />


## 6. Dateistruktur

```text
Display-I2C-HA-RP/
│
├── repository.json
└── i2c_display/
    │
    ├── config.yaml
    ├── Dockerfile
    ├── display.py
    ├── requirements.txt
    ├── run.sh
    └── README.md
```



