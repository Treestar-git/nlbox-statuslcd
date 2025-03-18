#!/bin/bash

REPO_URL="https://github.com/Treestar-git/nlbox-statuslcd.git"
SERVICE_NAME="status_lcd"

echo "🔄 Frissítés indítása..."

# Systemd szolgáltatás leállítása
echo "🛑 Szolgáltatás leállítása..."
sudo systemctl stop ${SERVICE_NAME}

# Legújabb verzió letöltése
echo "📥 Legújabb verzió letöltése a GitHub-ról..."
cd /home/pi
if [ -d "nlbox-statuslcd" ]; then
    cd nlbox-statuslcd
    git pull
else
    git clone ${REPO_URL}
    cd nlbox-statuslcd
fi

# Szolgáltatás újraindítása
echo "🚀 Új verzió indítása..."
sudo systemctl start ${SERVICE_NAME}

echo "✅ Frissítés befejezve!"
