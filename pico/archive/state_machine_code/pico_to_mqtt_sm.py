from micropython import const
import rp2
from rp2 import PIO, asm_pio

led = machine.Pin("LED", machine.Pin.OUT)
led.off()

# *********************************************
# MQTT connection
# *********************************************

import utime
import network
from umqtt.simple import MQTTClient
import time

wifi_name = "lbnl-visitor"
wifi_password = ""

mqtt_broker = "198.128.196.115"
mqtt_port = 1883
mqtt_topic = b"statemachine"

wifi_name = "602"
wifi_password = "F=ma1686"
mqtt_broker = "192.168.86.79"

# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to wifi...")
    wlan.connect(wifi_name, wifi_password)
    while not wlan.isconnected():
        time.sleep(1)
print(f"Connected to wifi {wifi_name}")

# Connect to MQTT broker
client = MQTTClient("thomas_pico_w_client", mqtt_broker, port=mqtt_port)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker}")

# *********************************************
# State machine code
# *********************************************
  
@asm_pio(sideset_init=PIO.OUT_HIGH)
def gate():
    """
    This PIO generates a gate signal.
    During the gating period (specified by osr), it keeps the gate signal low, then raises it high after the gating period ends.
    """
    # Loads the gate time (in clock pulses) from osr into the x register
    mov(x, osr)
    # Waits for a low to high transition (rising edge) on the input pin
    wait(0, pin, 0)
    wait(1, pin, 0)
    # Loop x times, keeping the gate low for that given time
    label("loopstart")
    jmp(x_dec, "loopstart") .side(0)
    # Waits for a low to high transition a (falling edge) on the input pin
    wait(0, pin, 0)
    # Sets the gate high on the rising edge of the input pin.
    wait(1, pin, 0) .side(1)
    # Interrupt handling
    irq(block, 0)                                          # set interrupt 0 flag and wait for system handler to service interrupt
    wait(1, irq, 4)                                        # wait for irq from clock counting state machine (IRQ4)
    wait(1, irq, 5)                                        # wait for irq from pulse counting state machine (IRQ5)


@asm_pio()
def clock_count():
    """PIO for counting clock pulses during gate low period."""
    mov(x, osr)                                            # load x scratch with max value (2^32-1)
    wait(1, pin, 0)                                        # detect falling edge
    wait(0, pin, 0)                                        # of gate signal
    label("counter")
    jmp(pin, "output")                                     # as long as gate is low //
    jmp(x_dec, "counter")                                  # decrement x reg (counting every other clock cycle - have to multiply output value by 2)
    label("output")
    mov(isr, x)                                            # move clock count value to isr
    push()                                                 # send data to FIFO
    irq(block, 4)                                          # set irq and wait for gate PIO to acknowledge

@asm_pio(sideset_init=PIO.OUT_HIGH)
def pulse_count():
    """PIO for counting incoming pulses during gate low."""
    mov(x, osr)                                            # load x scratch with max value (2^32-1)
    wait(1, pin, 0)                                        
    wait(0, pin, 0) .side(0)                               # detect falling edge of gate
    label("counter")
    wait(0, pin, 1)                                        # wait for rising
    wait(1, pin, 1)                                        # edge of input signal
    jmp(pin, "output")                                     # as long as gate is low //
    jmp(x_dec, "counter")                                  # decrement x req counting incoming pulses (probably will count one pulse less than it should - to be checked later)
    label("output") 
    mov(isr, x) .side(1)                                   # move pulse count value to isr and set pin to high to tell clock counting sm to stop counting
    push()                                                 # send data to FIFO
    irq(block, 5)                                          # set irq and wait for gate PIO to acknowledge


def init_sm(freq, input_pin, gate_pin, pulse_fin_pin):
    """Starts state machines."""
    gate_pin.value(1)
    pulse_fin_pin.value(1)
    max_count = const((1 << 32) - 1)
    
    # sm0 handles generating the gate signal.
    sm0 = rp2.StateMachine(0, gate, freq=freq, in_base=input_pin, sideset_base=gate_pin)
    sm0.put(freq)
    sm0.exec("pull()")
    
    # sm1 counts clock pulses during the gate low period.
    sm1 = rp2.StateMachine(1, clock_count, freq=freq, in_base=gate_pin, jmp_pin=pulse_fin_pin)
    sm1.put(max_count)
    sm1.exec("pull()")
    
    # sm2 counts incoming pulses during the gate low period.
    sm2 = rp2.StateMachine(2, pulse_count, freq=freq, in_base=gate_pin, sideset_base = pulse_fin_pin, jmp_pin=gate_pin)
    sm2.put(max_count-1)
    sm2.exec("pull()")
    
    sm1.active(1)
    sm2.active(1)
    sm0.active(1)
    
    return sm0, sm1, sm2

if __name__ == "__main__":
    
    from machine import Pin
    import uarray as array
    
    # Initialize
    update_flag = False
    data = array.array("I", [0, 0])
    
    # Define interrupt handler function
    def counter_handler(sm):
        print("\nIRQ")
        global update_flag
        if not update_flag:
            #sm0.put(12_500_000)
            sm0.put(125_000)
            sm0.exec("pull()")
            data[0] = sm1.get() # clock count
            data[1] = sm2.get() # pulse count
            update_flag = True
    
    # Initialize state machines and assign interrupt handler
    sm0, sm1, sm2 = init_sm(125_000_000, Pin(15, Pin.IN, Pin.PULL_UP), Pin(14, Pin.OUT), Pin(13, Pin.OUT))
    sm0.irq(counter_handler)
    
    # Testing
    print("Starting test")
    i = 0
    while True:
        if update_flag:
            
            # Get clock and pulse counts
            clock_count = 2*(max_count - data[0]+1)
            pulse_count = max_count - data[1]
            
            # Calculate frequency
            freq = pulse_count * (125000208.6 / clock_count)
            
            print(i)
            i += 1
            print("Clock count: {}".format(clock_count))
            print("Input count: {}".format(pulse_count))
            print("Frequency:   {}".format(freq))
            
            client.publish(mqtt_topic, str(freq))
            
            update_flag = False