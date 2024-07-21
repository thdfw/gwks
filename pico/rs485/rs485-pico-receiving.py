import machine
import utime

# Define RS-485 control pin
RE_DE_PIN = machine.Pin(15, machine.Pin.OUT)

# Turn off to receive messages
RE_DE_PIN.off()

# UART setup
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

while True:
    if uart.any():
        received = uart.read()
        print("Received:", received)
    utime.sleep(1)