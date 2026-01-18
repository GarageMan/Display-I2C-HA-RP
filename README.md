# I2C System Display Add-on

Dieses Home Assistant Add-on zeigt Systeminformationen auf einem 128x64 I2C OLED Display an:

- CPU-Auslastung
- RAM-Auslastung
- CPU-Temperatur
- Home Assistant Status
- Status-LED

## Installation

1. GitHub-Repository in Home Assistant hinzufügen:
   **Einstellungen → Add-ons → Add-on Store → Repositories → URL einfügen**

2. Add-on „I2C System Display“ installieren

3. I2C aktivieren:
   Supervisor → System → Hardware → I2C muss sichtbar sein  
   Falls nicht: Raspberry Pi → I2C im Bootloader aktivieren

4. Add-on starten

Das Display aktualisiert sich automatisch mit 1 Hz.


HA-I2C-Display/
├── repository.json
└── i2c_display/
    ├── config.yaml
    ├── Dockerfile
    ├── display.py
    ├── requirements.txt
    ├── README.md
    └── rootfs/
        └── etc/
            └── services.d/
                └── display/
                    ├── run
                    └── finish
