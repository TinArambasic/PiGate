import smbus2
import time

# PCA9685 registri
PCA9685_ADDRESS = 0x40
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

bus = smbus2.SMBus(1)

def write_byte(reg, value):
    bus.write_byte_data(PCA9685_ADDRESS, reg, value)

def set_pwm(channel, on, off):
    base = LED0_ON_L + 4 * channel
    bus.write_byte_data(PCA9685_ADDRESS, base, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, base + 1, on >> 8)
    bus.write_byte_data(PCA9685_ADDRESS, base + 2, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDRESS, base + 3, off >> 8)

def set_level(channel, value):
    if value == 1:
        set_pwm(channel, 4096, 0)
    else:
        set_pwm(channel, 0, 4096)

def set_duty(channel, duty):
    pulse = int(4096 * duty / 100)
    set_pwm(channel, 0, pulse)

# Init PCA9685
write_byte(MODE1, 0x00)
time.sleep(0.1)

# Kanali prema Waveshare dokumentaciji
PWMA = 0
AIN1 = 1
AIN2 = 2

def motor_forward(speed):
    set_duty(PWMA, speed)
    set_level(AIN1, 1)
    set_level(AIN2, 0)

def motor_backward(speed):
    set_duty(PWMA, speed)
    set_level(AIN1, 0)
    set_level(AIN2, 1)

def motor_stop():
    set_duty(PWMA, 0)
    set_level(AIN1, 0)
    set_level(AIN2, 0)

print("Naprijed 2 sekunde...")
motor_forward(50)
time.sleep(2)

print("Nazad 2 sekunde...")
motor_backward(50)
time.sleep(2)

print("Stop.")
motor_stop()
bus.close()
