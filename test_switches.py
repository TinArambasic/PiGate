from gpiozero import Button
from signal import pause

switch_open = Button(17, pull_up=True, bounce_time=0.1)
switch_closed = Button(27, pull_up=True, bounce_time=0.1)

def on_open_pressed():
    print("Switch OTVORENO aktiviran!")

def on_closed_pressed():
    print("Switch ZATVORENO aktiviran!")

switch_open.when_pressed = on_open_pressed
switch_closed.when_pressed = on_closed_pressed

print("Čekam pritisak na switcheve... (Ctrl+C za izlaz)")
pause()
