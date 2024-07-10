"""
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the hall sensor.
Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run this code on the Pico W (either call it main.py or through Thonny)
- Save the data to a CSV file live by running mqtt_to_csv.py
"""

import machine
import utime
import network
from umqtt.simple import MQTTClient
import time

# *********************************************
# PARAMETERS
# *********************************************

wifi_name = "ARRIS-3007"
wifi_password = "ADD SOMERSET PASSWD"

# 192.168.0.89 is the address for beech2 in somerset, which is set up to allow anonymous
mqtt_broker = "192.168.0.89"
mqtt_username = ""
mqtt_password = ""


mqtt_port = 1883
hall_mqtt_topic = b"hall_sensor"
ekm_mqtt_topic = b"ekm_sensor"

client_name = "pico_w"

HALL_PULSE_PIN = 28
EKM_PULSE_PIN = 29
# *********************************************
# Connecting to WiFi and MQTT broker
# *********************************************

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
client = MQTTClient(client_name, mqtt_broker, user=mqtt_username, password=mqtt_password, port=mqtt_port)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}")

# *********************************************
# Reading timestamps
# *********************************************

latest_ekm = 0

# Callback function to record the timestamp of each hall meter pulse
def hall_pulse_callback(pin, topic=hall_mqtt_topic):
    timestamp = utime.time_ns()
    client.publish(hall_mqtt_topic, f"{timestamp}")



def ekm_pulse_callback(pin):
    """
    Callback function to record the timestamp of each ekm meter pulse
    Ignore false positives in jitter happening under 5 milliseconds
    as the EKM meter will never have a pulse faster than twice a second
    
    """
    global latest_ekm
    timestamp = utime.time_ns()
    # ignore jitter at under 5 milliseconds
    if timestamp - latest_ekm > 5_000_000:
        latest_ekm = timestamp
        client.publish(ekm_mqtt_topic, f"{timestamp}")


# Set up the pin for input and attach interrupt for rising edge
hall_pulse_pin = machine.Pin(HALL_PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=hall_pulse_callback)

ekm_pulse_pin = machine.Pin(EKM_PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
ekm_pulse_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=ekm_pulse_callback)

try:
    while True:
        utime.sleep(10)
        
except KeyboardInterrupt:
    print("Program interrupted by user")