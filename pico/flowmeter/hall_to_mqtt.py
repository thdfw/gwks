"""
commit 3b2919c0 of https://github.com/thdfw/gwks/pico/flowmeter/hall_to_mqtt.py
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the hall sensor, on hall_sensor topic
Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run this code on the Pico W (either call it main.py or through Thonny)
- Save the data to a CSV file live by running mqtt_to_csv.py
"""

# Saving the previous log file content, then deleting the file
import uos
try:
    uos.stat('mqtt.log')
    log_file_exists = True
    with open('mqtt.log', 'r') as f:
        log_content = f.read()
    uos.remove('mqtt.log')
except OSError:
    log_file_exists = False

import machine
import utime
import network
from umqtt.simple import MQTTClient
import time
import ubinascii

node_name = "dist-flow"
HB_FREQUENCY_S = 3
# *********************************************
# TOPICS
# *********************************************

send_topic_hb = b"dist-flow/hb"
send_topic_tick = b"dist-flow/tick"
send_topic_hwuid = b"dist-flow/scada/hw-uid-response"
send_topic_log = b"dist-flow/log"

receive_topic_hwuid = b"scada/dist-flow/hw-uid-request"


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
mqtt_topic2 = b"hall_id"

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()
client_name = f"pico_w_{str(pico_unique_id)[-6:]}"

PULSE_PIN = 28

# *********************************************
# Publish unique ID on request
# *********************************************

def sub_callback(topic, msg):
    if topic==receive_topic_hwuid:
        client.publish(send_topic_hwuid, f'Pico unique ID: {pico_unique_id}')

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
client.subscribe(receive_topic_hwuid)
print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}, and subscribed to {receive_topic_hwuid}")

# Publish a first timestamp
client.publish(send_topic_tick, f"Calibration timestamp from {client_name}: {utime.time_ns()}")

# Publish the content of the previous log file
if log_file_exists:
    client.publish(send_topic_log, f'{log_content}')
    print(f"Published previous log file to topic {send_topic_log}")

# *********************************************
# Reading timestamps
# *********************************************

latest = 0
count_hall_ticks = 0

# Callback function to record the timestamp of each hall meter pulse
def pulse_callback(pin, topic=mqtt_topic):
    """
    Callback function to record the timestamp of each hall meter tick 
    and send by mqtt. Sends on topic dist-flow/tick
    """
    global latest
    global count_hall_ticks
            
    timestamp = utime.time_ns()
    latest = timestamp
    
    client.publish(send_topic_tick , f"{timestamp}")
    
    count_hall_ticks += 1
    if count_hall_ticks > 1000:
        with open('ticks.csv', 'w') as file:
            file.write(f'{timestamp}\n')
        count_hall_ticks = 0

# Set up the pin for input and attach interrupt for rising edge
hall_pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

# *********************************************
# Publish Heartbeat
# *********************************************
hb = 0


# Publish a heartbeat, assuming no tick in the last 3 seconds. Acts as a keepalive
def publish_heartbeat(timer):
    global hb
    global latest
    hb = (hb + 1) % 16
    hbstr = "{:x}".format(hb)
    msg =   {'MyHex': hbstr, 'TypeName': 'hb', 'Version': '000'}
    timestamp = utime.time_ns()
    if (timestamp - latest) / 10**9 > HB_FREQUENCY_S:
        client.publish(send_topic_hb, str(msg))


# Create a timer to publish heartbeat every 3 seconds
heartbeat_timer = machine.Timer(-1)
heartbeat_timer.init(period=HB_FREQUENCY_S * 1000, mode=machine.Timer.PERIODIC, callback=publish_heartbeat)



try:
    while True:
        # Check for request messages on the topic
        client.check_msg()
        utime.sleep(5)
except KeyboardInterrupt:
    print("Program interrupted by user")
    heartbeat_timer.deinit()