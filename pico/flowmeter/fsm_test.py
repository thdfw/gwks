from machine import Pin
import rp2
import time

# Define the PIO program for measuring the time between rising edges
@rp2.asm_pio()
def measure_time():
    wait(1, pin, 0)  # Wait for the first rising edge
    mov(x, osr)      # Store the counter value
    wait(1, pin, 0)  # Wait for the second rising edge
    mov(isr, x)      # Store the time difference in ISR
    push(block)      # Push ISR value to RX FIFO
    jmp(0)           # Repeat

# Initialize the state machine
def init_sm(freq, input_pin):
    sm = rp2.StateMachine(0, measure_time, freq=freq, in_base=input_pin)
    sm.active(1)
    return sm

# Callback function to handle the interrupt
def frequency_callback(sm):
    global last_measurement_time
    period_cycles = sm.get()  # Get the duration in clock cycles
    frequency = 125_000_000 / period_cycles  # Convert to frequency
    print(f"Frequency: {frequency:.2f} Hz")
    last_measurement_time = time.ticks_ms()  # Update last measurement time

# Main function
if __name__ == "__main__":
    input_pin = Pin(28, Pin.IN)
    sm = init_sm(125_000_000, input_pin)  # Initialize state machine with 125 MHz clock

    # Attach the IRQ handler
    sm.irq(handler=lambda sm: frequency_callback(sm))

    # Main loop
    try:
        while True:
            time.sleep(1)  # Sleep to allow callbacks to be processed
    except KeyboardInterrupt:
        print("Program stopped")