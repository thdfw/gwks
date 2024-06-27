"""
Example using PIO to blink an LED and raise an IRQ at 1Hz
"""

import time
from machine import Pin
import rp2

"""
The decorator specifies that blink_1hz is written in PIO assembly language
The pins are initialized to a low state (0)
"""
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_1hz():
    
    # ************************************************
    # Cycles: 1 + 1 + 6 + 32 * (30 + 1) = 1000 cycles
    # ************************************************

    # Generate an interrupt request (IRQ) immediately (rel(0))
    irq(rel(0)) # 1 cycle

    # Set the pins controlled by this program to a high state (1) => LED on
    set(pins, 1) # 1 cycle

    '''
    This is a loop that repeats 32 times.
    Register x starts at 31, and is decremented until et reaches 0.
    nop() means "no operation", takes a cycle without doing anything.
    '''
    set(x, 31) [5]              # 1 cycle set, 5 cycle delay
    label("delay_high")         # 0 cycle
    nop() [29]                  # 30 cycle delay
    jmp(x_dec, "delay_high")    # 1 cycle

    # ************************************************
    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000 cycles
    # ************************************************

    # Set the pins controlled by this program to a low state (0) => LED off
    set(pins, 0)

    set(x, 31) [6]              # 1 cycle set, 6 cycle delay
    label("delay_low")          # 0 cycle
    nop() [29]                  # 30 cycle delay
    jmp(x_dec, "delay_low")     # 1 cycle


"""
Create the StateMachine
- With number 0 (the first StateMachine)
- With the blink_1hz program
- With a clock frequency of 2000 cycles per second
=> So 1000 cycles is effectively half a second, blink at 1Hz
- Outputting on Pin(16)
"""
sm = rp2.StateMachine(0, blink_1hz, freq=2000, set_base=Pin(16))

# Set the IRQ handler to print the millisecond timestamp when an IRQ is called
sm.irq(lambda p: print(time.ticks_ms()))

# Start the StateMachine
sm.active(1)