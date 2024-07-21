import machine
import utime

RE_DE_PIN = machine.Pin(15, machine.Pin.OUT)
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
RE_DE_PIN.on()  # Enable transmit mode
utime.sleep(0.5)

while True:
    uart.write("Hello from Pico W!\n")
    print('Hello')
    utime.sleep(0.5)