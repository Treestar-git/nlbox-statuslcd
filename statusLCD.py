import time
import psutil
import socket
import fcntl
import struct
import subprocess
import signal
import sys
from datetime import datetime
from smbus2 import SMBus
from RPLCD.i2c import CharLCD

# LCD kijelző beállításai
lcd = None

# Sorozatszám fájl elérési útja
SERIAL_FILE = "/etc/statuslcd/serial"


# Sorozatszám beolvasása fájlból
def get_serial_number():
    try:
        with open(SERIAL_FILE, "r") as file:
            serial = file.readline().strip()
            return serial if serial else "No serial"
    except FileNotFoundError:
        return "No serial"



# Docker konténer állapot lekérése
def get_container_status(container_name):
    try:
        # Lekérdezzük a konténer állapotát (megkeressük az adott nevű konténert)
        result = subprocess.run(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.State}}"], 
                                stdout=subprocess.PIPE, text=True)
        
        state = result.stdout.strip()

        # Státusz meghatározása
        if state == "running":
            return "RUNNING"
        elif state in ["exited", "created", "paused", "restarting"]:
            return "STOPPED"
        else:
            return "MISSING"
    
    except Exception as e:
        return "ERROR"

# Konténer státusz kiíratása
def print_container_stat(name, module_name, row):
    global lcd
    status = get_container_status(name)
            
    # Kiírás az LCD-re
    lcd.cursor_pos = (row, 0)
    lcd.write_string(f"{module_name[:8]}: {status}  ")  # Levágjuk, ha hosszú a név


def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR - Interfész IP címének lekérése
            struct.pack('256s', ifname.encode('utf-8')[:15])  # Python 3 kompatibilis
        )[20:24])
    except OSError:
        return "Nincs IP"


# CPU hőmérséklet lekérése
def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000  # Celsius fok
        return f"{temp:.1f}°C"
    except:
        return "N/A"

# CPU és RAM terheltség lekérése
def get_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    ram_usage = memory.percent
    return cpu_usage, ram_usage

# Dátum és idő lekérése
def get_datetime():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")  # Pl.: 2024-02-14
    time_str = now.strftime("%H:%M")  # Pl.: 14:35:21
    return date_str, time_str

# Dátum és idő megjelenítése
def print_datetime():
    global lcd
    date_str, time_str = get_datetime()
    lcd.clear()
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f"{date_str}     ")
    lcd.cursor_pos = (0, 0)
    lcd.write_string(f"{time_str}       ")

# LCD csatlakozásának ellenőrzése
def connect_lcd():
    global lcd
    while True:
        try:
            lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                          cols=16, rows=2, charmap='A02', auto_linebreaks=True)
            lcd.clear()
            lcd.write_string("LCD Ready...")
            time.sleep(1)
            return  # Sikeres csatlakozás esetén kilép
        except Exception:
            print("LCD nem elérhető, várakozás újracsatlakozásra...")
            time.sleep(2)  # Próbálkozás 5 másodpercenként


# ** KILÉPÉSKOR ÜZENET KIÍRÁSA ** #
def exit_handler(signal_received=None, frame=None):
    global lcd
    if lcd:
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("SYSTEM SHUTDOWN")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("Goodbye!       ")
    print("⚠️  Rendszer vagy script leáll. LCD üzenet kiírva.")
    sys.exit(0)


# Adatok kijelzése
def display_data():
    global lcd
    lcd.clear()
    lcd.write_string("Welcome")  # Első sor
    time.sleep(3)

    while True:

        # Ha az LCD bármikor megszakad, újracsatlakozunk
        while lcd is None:
            connect_lcd()

        try:

            # Készülék adatok megjelenítése
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("NewLine Kft.")  # Első sor
            lcd.cursor_pos = (1, 0)
            lcd.write_string("NLBOX Rev. 1-A")  # Második sor
            time.sleep(3)

            # Sorozatszám megjelenítése
            lcd.clear()
            serial_number = get_serial_number()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("Serial number:")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f"{serial_number[:16]}")  # Max 16 karakter
            time.sleep(3)

            # Dátum-idő kiírása
            print_datetime()
            time.sleep(3)

            # IP-cím és CPU temp kiírása
            lcd.clear()
            temp = get_cpu_temp()
            ip = get_ip_address('eth0')
            lcd.cursor_pos = (0, 0)
            lcd.write_string(f"CPU Temp:{temp:<7}")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f"{ip:<16}")
            time.sleep(3)

            # CPU és RAM használat
            cpu, ram = get_system_usage()
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(f"CPU:{cpu:4.1f}%")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f"RAM:{ram:4.1f}%")
            time.sleep(3)

            # Docker konténerek állapota
            lcd.clear()
            print_container_stat("pis", "PIS", 0)
            print_container_stat("vdu", "VDU", 1)
            time.sleep(3)

            lcd.clear()
            print_container_stat("ddu", "DDU", 0)
            print_container_stat("rabbitmq-rabbitmq-1", "MQTT", 1)
            time.sleep(3)


        except Exception:
            print("LCD kapcsolat megszakadt, újrapróbálkozás...")
            lcd = None  # LCD kapcsolat megszakadt, meg kell próbálni újracsatlakozni


# Fő program
try:
    # Kilépéskor figyeljük a jeleket
    signal.signal(signal.SIGTERM, exit_handler)  # Rendszerleállítás jele
    signal.signal(signal.SIGINT, exit_handler)   # Manuális leállítás (Ctrl+C)

    connect_lcd()
    display_data()
except KeyboardInterrupt:
    exit_handler()
