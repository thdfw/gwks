"""
Read ticks in nanoseconds from pin 28 and write ~1200 ticks to a local
csv on the pico. 

For setting up a pico attached to a Saeir flow meter, see 
https://docs.google.com/document/d/1fVRBN6Pm6bmA-EqMnx1Lw3zIszstL6nPF1oPlRDzGIQ/edit
"""
import machine
import utime

# If this is more than about 1200 the pico can have trouble with memory.
PULSES_BEFORE_WINDING_DOWN = 1200

PULSE_PIN = 28
timestamps = []

def pulse_callback(pin):
    global timestamps
    timestamp = utime.time_ns()
    timestamps.append(timestamp)
    
# Set up the pin for input and attach interrupt for rising edge
pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

utime.sleep(1)

try:
    while len(timestamps) < PULSES_BEFORE_WINDING_DOWN:
        if len(timestamps) > 1:
            hz = 1e9/(timestamps[-1] - timestamps[-2])
            formatted_hz =  round(hz,2)
            print(f"{formatted_hz} Hz, Pulse count: {len(timestamps)}")
        else:
            print("No pulses detected yet.")
        utime.sleep(3)

except KeyboardInterrupt:
    print("Program interrupted by user")


# Save timestamps to a CSV file
with open("timestamps.csv", "w") as csvfile:
    csvfile.write("timestamp_ns\n")
    for timestamp in timestamps:
        csvfile.write(f"{timestamp}\n")
print("Timestamps saved to timestamps.csv")

# Clean up the interrupt
pulse_pin.irq(handler=None)