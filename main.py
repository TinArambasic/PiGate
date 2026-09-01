import time
import threading
import smbus2
from gpiozero import Button, LED
from picamera2 import Picamera2
from fast_alpr import ALPR
import cv2
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, '/home/tin/gate-system/app')
from database import init_db, is_plate_allowed, log_access
import app as web_app

#GPIO konfiguracija 
SWITCH_OPEN_PIN   = 17
SWITCH_CLOSED_PIN = 27
GREEN_LED_PIN     = 22
RED_LED_PIN       = 23

switch_open   = Button(SWITCH_OPEN_PIN,   pull_up=True, bounce_time=0.1)
switch_closed = Button(SWITCH_CLOSED_PIN, pull_up=True, bounce_time=0.1)
green_led     = LED(GREEN_LED_PIN)
red_led       = LED(RED_LED_PIN)

#Motor konfiguracija
PCA9685_ADDRESS = 0x40
LED0_ON_L       = 0x06
bus             = smbus2.SMBus(1)
PWMA, AIN1, AIN2 = 0, 1, 2

def pca_write(reg, val):
    bus.write_byte_data(PCA9685_ADDRESS, reg, val)

def set_pwm(ch, on, off):
    b = LED0_ON_L + 4 * ch
    bus.write_byte_data(PCA9685_ADDRESS, b,     on  & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, b + 1, on  >> 8)
    bus.write_byte_data(PCA9685_ADDRESS, b + 2, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, b + 3, off >> 8)

def set_level(ch, val):
    set_pwm(ch, 4096, 0) if val else set_pwm(ch, 0, 4096)

def set_duty(ch, duty):
    set_pwm(ch, 0, int(4096 * duty / 100))

pca_write(0x00, 0x00)
time.sleep(0.1)

def motor_forward(speed=60):
    set_duty(PWMA, speed); set_level(AIN1, 1); set_level(AIN2, 0)

def motor_backward(speed=60):
    set_duty(PWMA, speed); set_level(AIN1, 0); set_level(AIN2, 1)

def motor_stop():
    set_duty(PWMA, 0); set_level(AIN1, 0); set_level(AIN2, 0)

#Kamera i ALPR
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (2304, 1296)}))
picam2.start()
time.sleep(2)
picam2.set_controls({"AfMode": 2, "AfTrigger": 0})  # Continuous autofocus
time.sleep(2)

alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

#Stanje sustava
gate_busy = False

OPEN_TIME  = 14.32
CLOSE_TIME = 15.10

def open_gate():
    global gate_busy
    gate_busy = True
    print("Otvaranje vrata...")
    motor_backward()
    time.sleep(OPEN_TIME)
    motor_stop()
    print("Vrata otvorena.")
    time.sleep(5)
    close_gate()

def close_gate():
    global gate_busy
    print("Zatvaranje vrata...")
    motor_forward()
    time.sleep(CLOSE_TIME)
    motor_stop()
    print("Vrata zatvorena.")
    gate_busy = False

def scan_plate():
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    preview = cv2.resize(frame, (640, 360))
    cv2.imwrite('/tmp/pigate_frame.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 50])
    results = alpr.predict(frame)
    if not results:
        return None, 0.0
    best = max(results, key=lambda p: sum(p.ocr.confidence) / len(p.ocr.confidence))
    confidence = sum(best.ocr.confidence) / len(best.ocr.confidence)
    return best.ocr.text, confidence

#Main loop
init_db()
print("PiGate sustav pokrenut. Čekam vozilo...")

CONFIDENCE_THRESHOLD = 0.7

try:
    while True:
        # Provjeri manual komandu od web app
        try:
            with open('/tmp/gate_command', 'r') as f:
                cmd = f.read().strip()
            open('/tmp/gate_command', 'w').close()
            if cmd == 'open' and not gate_busy:
                t = threading.Thread(target=open_gate)
                t.start()
            elif cmd == 'close' and not gate_busy:
                t = threading.Thread(target=close_gate)
                t.start()
        except FileNotFoundError:
            pass

        if gate_busy:
            time.sleep(0.5)
            continue

        plate, confidence = scan_plate()

        if plate:
            print(f"Vidim tablicu: {plate} | Confidence: {confidence:.2f}")
        if plate and confidence >= CONFIDENCE_THRESHOLD:
            print(f"Detektirana tablica: {plate} ({confidence:.2f})")
            allowed = is_plate_allowed(plate)
            log_access(plate, allowed, confidence)

            if allowed:
                print(f"Tablica {plate} dozvoljena — otvaranje vrata!")
                green_led.on()
                red_led.off()
                t = threading.Thread(target=open_gate)
                t.start()
                time.sleep(3)
                green_led.off()
            else:
                print(f"Tablica {plate} nije dozvoljena!")
                red_led.blink(on_time=0.3, off_time=0.3, n=5)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Zaustavljanje sustava...")
    motor_stop()
    green_led.off()
    red_led.off()
    bus.close()
    picam2.stop()
    print("Sustav zaustavljen.")
