import time
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

'''
Pin 7 of Pi is connected to DE & RE of RS-485.
Turn it on (high) to enable sending values to RS-485.
'''
GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH)

ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

i = [0,10,45,90,135,180,135,90,45,10,0]

while True:
    for x in i:
        ser.write(str(x).encode('utf-8'))
        print(x)
        time.sleep(2)