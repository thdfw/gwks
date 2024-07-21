import time
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

'''
Pin 7 of Pi is connected to DE & RE of RS-485. 
Turn it off (low) to receive from RS-485.
'''
GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)

ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2
)

try:
    while True:
        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8', errors='replace').rstrip()
            print("Received:", received)
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    ser.close()