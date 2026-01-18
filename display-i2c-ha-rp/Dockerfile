ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-python:3.12-alpine3.19
FROM $BUILD_FROM

# Deaktiviere das s6-overlay System explizit
ENV S6_OVERLAY_VERSION=0
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2

# System-Abhängigkeiten (build-base etc. für luma.oled/Pillow)
RUN apk add --no-cache \
    i2c-tools \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev

WORKDIR /app

# Python-Pakete installieren
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Skripte kopieren
COPY i2c-display.py .
COPY run.sh /
RUN chmod a+x /run.sh

# Wir nutzen ENTRYPOINT, um s6 komplett zu umgehen
ENTRYPOINT ["/bin/bash", "/run.sh"]
