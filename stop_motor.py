import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

#Ugasi sve kanale
for channel in pca.channels:
    channel.duty_cycle = 0

pca.deinit()
print("Motor zaustavljen.")
