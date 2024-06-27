import machine
import utime

HALL_PULSE_PIN = 15
timestamps = []

def hall_pulse_callback(pin):
    global timestamps
    timestamp = utime.time_ns()
    timestamps.append(f"{timestamp}, Hall")
    
# Set up the pin for input and attach interrupt for rising edge
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

finally:
    
    # Save timestamps to a CSV file
    with open("timestamps.csv", "w") as csvfile:
        csvfile.write("timestamp_ns\n")
        for timestamp in timestamps:
            csvfile.write(f"{timestamp}\n")
    print("Timestamps saved to timestamps.csv")

    # Clean up the interrupt
    hall_pulse_pin.irq(handler=None)