ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM $BUILD_FROM

# Abhängigkeiten installieren
RUN apk add --no-cache \
    python3 \
    py3-pip \
    i2c-tools \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev

WORKDIR /app

# Python Pakete
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Skripte kopieren
COPY display.py .
COPY run.sh /
RUN chmod a+x /run.sh

# DAS IST DER ENTSCHEIDENDE TEIL:
# Wir überschreiben NICHT den Entrypoint des Base-Images,
# sondern nutzen CMD, um unser Skript dem s6-init-System zu übergeben.
CMD [ "/run.sh" ]
