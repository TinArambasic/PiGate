from gpiozero import LED
import time

green = LED(22)
red = LED(23)

print("Zelena ON...")
green.on()
time.sleep(1)
green.off()

print("Crvena blink 3x...")
for _ in range(3):
    red.on()
    time.sleep(0.3)
    red.off()
    time.sleep(0.3)

print("Test završen.")
