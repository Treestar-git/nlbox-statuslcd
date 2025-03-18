#!/bin/bash

SERVICE_NAME="status_lcd"
SCRIPT_PATH="/home/pi/nlbox-statuslcd/statusLCD.py"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SERIAL_FILE="/etc/statuslcd/serial"
RPLCD_REPO="https://github.com/dbrgn/RPLCD.git"
RPLCD_DIR="/home/pi/RPLCD"

echo "📥 Telepítés indítása..."

# Szükséges csomagok telepítése
echo "🔄 Csomagok frissítése..."
sudo apt update
sudo apt install -y i2c-tools ptyhon3-smbus2 python3-psutil

# 📦 Ellenőrizzük, hogy az RPLCD telepítve van-e
if python -c "import RPLCD" &> /dev/null; then
    echo "✅ RPLCD már telepítve van."
else
    echo "📥 RPLCD nincs telepítve, letöltés GitHub-ról..."
    if [ -d "$RPLCD_DIR" ]; then
        cd $RPLCD_DIR
        git pull
    else
        git clone $RPLCD_REPO $RPLCD_DIR
        cd $RPLCD_DIR
    fi
    echo "🚀 RPLCD telepítése..."
    sudo python setup.py install
fi



# 📁 Serial fájl létrehozása
echo "📁 Sorozatszám fájl ellenőrzése..."
sudo mkdir -p /etc/statuslcd
if [ ! -f "$SERIAL_FILE" ]; then
    echo "📝 Alapértelmezett sorozatszám beállítása: Empty S/N"
    echo "Empty S/N" | sudo tee ${SERIAL_FILE} > /dev/null
else
    echo "✅ A sorozatszám fájl már létezik."
fi

# systemd szolgáltatás létrehozása
echo "⚙️ Systemd szolgáltatás létrehozása..."
sudo tee ${SERVICE_FILE} > /dev/null <<EOL
[Unit]
Description=LCD Display Script
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 ${SCRIPT_PATH}
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

# systemd szolgáltatás engedélyezése
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "✅ Telepítés kész! Az LCD kijelző szolgáltatás elindult."
