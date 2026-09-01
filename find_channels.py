import board
import busio
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685
import time

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

for i in range(0, 14, 2):
    print(f"Testiram kanale {i} i {i+1}...")
    try:
        m = motor.DCMotor(pca.channels[i], pca.channels[i+1])
        m.throttle = 0.5
        time.sleep(1.5)
        m.throttle = -0.5
        time.sleep(1.5)
        m.throttle = 0
        print(f"Kanali {i} i {i+1} - OK")
    except Exception as e:
        print(f"Kanali {i} i {i+1} - Error: {e}")
    time.sleep(0.5)

pca.deinit()
print("Test završen.")
