import machine
import utime

uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

while True:
    uart.write("Hello from Pico W!\n")
    print('Sent')
    utime.sleep(1)