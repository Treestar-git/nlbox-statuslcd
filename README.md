# Maestro Status LCD

Ez a projekt egy **2x16 karakteres LCD kijelzőn** jeleníti meg a **dátumot, időt, Docker konténerek állapotát és egyedi sorozatszámot**.

## 📥 Telepítés
1. **GitHub-ról klónozás:**
   ```bash
   git clone https://github.com/Treestar-git/nlbox-statuslcd.git
   cd nlbox-statuslcd

2. **Beállítás automatikus induláshoz:**
   ```bash
   chmod +x setup.sh
   ./setup.sh

3. **Sorozatszám beállítása:**
   ```bash
   sudo nano /etc/statuslcd/serial

4. **Frissítés:**
   ```bash
   chmod +x update.sh
   ./update.sh

5. **Állapot ellenőrzése:**
   ```bash
   sudo systemctl status status_lcd

6. **Kézi működtetés:**
   ```bash
   sudo systemctl start status_lcd
   sudo systemctl stop status_lcd

6. **Szolgáltatás letörlése:**
   ```bash
   chmod +x uninstall.sh
   ./uninstall.sh

7. **Hibaelhárítás:**
   Napló/Log megnézése
   ```bash
   journalctl -u status_lcd --no-pager --lines=50
