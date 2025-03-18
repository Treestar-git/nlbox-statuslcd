#!/bin/bash

SERVICE_NAME="status_lcd"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_PATH="/home/pi/nlbox-statuslcd/statusLCD.py"
SERIAL_FILE="/home/pi/serial.txt"

echo "🛑 LCD kijelző szolgáltatás eltávolítása..."

# 🔴 Systemd szolgáltatás leállítása és törlése
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo "🛑 Szolgáltatás leállítása..."
    sudo systemctl stop ${SERVICE_NAME}
fi

if systemctl is-enabled --quiet ${SERVICE_NAME}; then
    echo "🛑 Szolgáltatás letiltása..."
    sudo systemctl disable ${SERVICE_NAME}
fi

if [ -f "$SERVICE_FILE" ]; then
    echo "🗑 Szolgáltatás fájl törlése..."
    sudo rm ${SERVICE_FILE}
fi

# 🔄 Systemd újratöltése
sudo systemctl daemon-reload

# 🧹 Naplófájlok törlése
echo "🗑 Naplók törlése..."
sudo journalctl --vacuum-time=1s

echo "✅ Az LCD kijelző szolgáltatás sikeresen eltávolítva!"