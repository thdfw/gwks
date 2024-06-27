import machine
import utime
import uos

HALL_PULSE_PIN = 16

uart = machine.UART(0, baudrate=115200, tx=machine.Pin(HALL_PULSE_PIN))
uos.dupterm(uart)

timestamps = []

def hall_pulse_callback(pin):
    global timestamps
    timestamp = utime.time_ns()
    timestamps.append(timestamp)
    print(timestamp)

hall_pulse_pin = machine.Pin(HALL_PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=hall_pulse_callback)

try:
    while True:
        if timestamps:
            last_timestamp = timestamps[-1]
            print(f"Pulse count: {len(timestamps)}, Last timestamp: {last_timestamp} (ns)")
        else:
            print("No pulses detected yet.")
        utime.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted by user")