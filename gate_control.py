import smbus2
import time
from gpiozero import Button

PCA9685_ADDRESS = 0x40
LED0_ON_L = 0x06
bus = smbus2.SMBus(1)
PWMA, AIN1, AIN2 = 0, 1, 2

switch_open = Button(17, pull_up=True, bounce_time=0.1)
switch_closed = Button(27, pull_up=True, bounce_time=0.1)

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

def motor_forward(speed=60):
    set_duty(PWMA, speed); set_level(AIN1, 1); set_level(AIN2, 0)

def motor_backward(speed=60):
    set_duty(PWMA, speed); set_level(AIN1, 0); set_level(AIN2, 1)

def motor_stop():
    set_duty(PWMA, 0); set_level(AIN1, 0); set_level(AIN2, 0)

def open_gate():
    motor_forward()
    while not switch_open.is_pressed:
        time.sleep(0.05)
    motor_stop()

def close_gate():
    motor_backward()
    while not switch_closed.is_pressed:
        time.sleep(0.05)
    motor_stop()
