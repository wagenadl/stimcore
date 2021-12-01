#!/usr/bin/python3

try:
    import RPi.GPIO as gp
    gp.setmode(gp.BCM)
    print('Raspberry Pi GPIO enabled')
    got = True
except:
    print('Raspberry Pi GPIO not enabled')
    got = False

def make_output(pin):
    if got:
        gp.setup(pin, gp.OUT)
    else:
        print(f'gpio {pin}')

def write(pin, val):
    if got:
        gp.output(pin, val)
    else:
        print(f'gpio {pin} -> {val}')
