# PiGate

Automatski sustav otvaranja ograde temeljen na prepoznavanju tablica vozila, izrađen na Raspberry Pi 5.
Test prototipa i demonstracija funkcionalnosti dostupna je na https://www.youtube.com/watch?v=2ENTelC4J9A

## O projektu

PiGate je prototip sustava koji kamerom snima vozilo koje se približava ogradi, prepoznaje tablicu vozila putem AI modela te automatski otvara ogradu ako je tablica u bazi dozvoljenih vozila. Sustavom se upravlja putem web aplikacije dostupne s bilo kojeg uređaja.

## Hardver

- Raspberry Pi 5 (4GB/8GB RAM)
- Raspberry Pi Camera Module 3
- Waveshare Motor Driver HAT (model 15364)
- DC elektromotor s reduktorom (12V, 30 RPM)
- Mehanizam zupčanik-letva (rack and pinion, modul M3)
- 2× mikroprekidač KW11-3Z
- 2× metalni LED indikator (zeleni + crveni)
- Napajanje 12V/2A

## Softver

- **Python 3** — glavna upravljačka logika
- **fast-alpr** — prepoznavanje tablica vozila (YOLO v9 + CCT OCR)
- **Flask** — web aplikacija
- **SQLite** — baza podataka
- **Cloudflare Tunnel** — pristup izvana
- **systemd** — automatsko pokretanje servisa

## Struktura projekta

```
gate-system/
├── main.py              # Glavna upravljačka logika
├── gate_control.py      # Upravljanje motorom
├── stop_motor.py        # Hitno zaustavljanje motora
├── camera_alpr.py       # Test skripta za kameru i ALPR
├── test_switches.py     # Test skripta za prekidače
├── test_leds.py         # Test skripta za LED indikatore
├── test_motor.py        # Test skripta za motor
└── app/
    ├── app.py           # Flask web aplikacija
    ├── database.py      # SQLite baza podataka
    └── templates/
        ├── index.html   # Stranica za upravljanje tablicama
        └── logs.html    # Stranica za pregled logova
```

## Instalacija

### 1. Kloniraj repozitorij

```bash
git clone https://github.com/TinArambasic/PiGate.git
cd PiGate
```

### 2. Instaliraj ovisnosti

```bash
sudo apt install python3-pip python3-libcamera python3-picamera2 python3-opencv i2c-tools -y
sudo pip install fast-alpr[onnx] flask smbus2 --break-system-packages
```

### 3. Aktiviraj I2C

```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

### 4. Postavi systemd servise

```bash
sudo systemctl daemon-reload
sudo systemctl enable pigate-main pigate-web pigate-tunnel
sudo systemctl start pigate-main pigate-web pigate-tunnel
```

## GPIO pinovi

| Komponenta | GPIO pin | Fizički pin |
|---|---|---|
| Switch (otvoreno) | GPIO 17 | Pin 11 |
| Switch (zatvoreno) | GPIO 27 | Pin 13 |
| LED zelena | GPIO 22 | Pin 15 |
| LED crvena | GPIO 23 | Pin 16 |

## Web aplikacija

Web aplikacija dostupna je lokalno na `http://<IP>:5000` ili putem interneta na `https://pigate.live`.

Funkcionalnosti:
- Dodavanje i brisanje dozvoljenih tablica vozila
- Pregled zapisa svih pokušaja pristupa
- Live video prijenos s kamere
- Ručno otvaranje i zatvaranje ograde

## Kako radi

1. Kamera kontinuirano snima ulazno područje
2. YOLO v9 model detektira tablicu vozila na slici
3. CCT OCR model prepoznaje znakove na tablici
4. Prepoznata tablica se uspoređuje s bazom dozvoljenih vozila
5. Ako je tablica dozvoljena → zelena LED + motor otvara ogradu
6. Ako tablica nije dozvoljena → crvena LED treperi
7. Nakon 5 sekundi ograda se automatski zatvara

## Licenca

MIT
