"""
commit XXXXXXXX of https://github.com/thdfw/gwks/
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the hall sensor, on hall_sensor topic
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
import ubinascii

hb_topic = b"dist-flow/hb"
hb =  {'MyHex': '0', 'YourLastHex': '0', 'TypeName': 'heartbeat.a', 'Version': '100'}

# *********************************************
# PARAMETERS
# *********************************************

wifi_name = "ARRIS-3007"
wifi_password = "ADD PASSWORD"

# Address for beech2 in somerset
mqtt_broker = "192.168.0.89"
mqtt_username = ""
mqtt_password = ""

mqtt_port = 1883
mqtt_topic = b"hall_sensor"

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()
client_name = f"pico_w_{str(pico_unique_id)[-6:]}"

PULSE_PIN = 28

# *********************************************
# Publish unique ID on request
# *********************************************

def sub_callback(topic, msg):
    message = msg.decode('utf-8')
    topic = topic.decode('utf-8')
    if message=="Request for unique_id" and topic==mqtt_topic:
        client.publish(mqtt_topic, f'Pico unique ID: {pico_unique_id}')

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

# Connect to MQTT broker and subscribe to topic
client = MQTTClient(client_name, mqtt_broker, user=mqtt_username, password=mqtt_password, port=mqtt_port)
client.set_callback(sub_callback)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}, and subscribed to {mqtt_topic}")
client.subscribe(mqtt_topic)

# Publish a first timestamp
client.publish(mqtt_topic, f"Calibration timestamp from {client_name}: {utime.time_ns()}")

# *********************************************
# Reading timestamps
# *********************************************

# Callback function to record the timestamp of each hall meter pulse
def pulse_callback(pin, topic=mqtt_topic):
    timestamp = utime.time_ns()
    client.publish(mqtt_topic, f"{timestamp}")

# Set up the pin for input and attach interrupt for rising edge
hall_pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

# *********************************************
# Publish Heartbeat
# *********************************************

def publish_heartbeat(timer):
    client.publish(hb_topic, str(hb))

# Create a timer to publish heartbeat every 3 seconds
heartbeat_timer = machine.Timer(-1)
heartbeat_timer.init(period=3000, mode=machine.Timer.PERIODIC, callback=publish_heartbeat)


try:
    while True:
        # Check for request messages on the topic
        client.check_msg()
        utime.sleep(5)
except KeyboardInterrupt:
    print("Program interrupted by user")
    heartbeat_timer.deinit()