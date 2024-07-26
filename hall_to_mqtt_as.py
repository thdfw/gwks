# Read existing log file and delete it
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
import time
import ubinascii
from mqtt_as import MQTTClient, config
import asyncio
import uasyncio

# Print diagnostic messages
MQTTClient.DEBUG = True

# Create loops for async functions
loop_heartbeat = uasyncio.get_event_loop()
loop_id = uasyncio.get_event_loop()

# *********************************************
# Parameters
# *********************************************

wifi_name = "ARRIS-3007"
wifi_password = "ADD PASSWORD"

mqtt_broker = "192.168.0.89"
mqtt_username = ""
mqtt_password = ""

HB_FREQUENCY_S = 3
PULSE_PIN = 28

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()
client_name = f"pico_w_{str(pico_unique_id)[-6:]}"

timestamps_to_send = []

# *********************************************
# Topics
# *********************************************

send_topic_hb = "dist-flow/hb"
send_topic_tick = "dist-flow/tick"
send_topic_hwuid = "dist-flow/hw-uid-response"
send_topic_log = "dist-flow/log"

receive_topic_hwuid = "scada/dist-flow/hw-uid-request"

# *********************************************
# Functions
# *********************************************

async def async_subscription_callback(topic, msg, retained):
    # print((topic, msg, retained))
    if topic == receive_topic_hwuid:
        await client.publish(send_topic_hwuid, f'Pico unique ID: {pico_unique_id}', qos=1)

def subscription_callback(topic, msg, retained):
    loop_id.create_task(async_subscription_callback(topic, msg, retained))

loop_id.run_forever()

async def on_connect(client):
    # Subscribe to topics
    await client.subscribe(receive_topic_hwuid, 1)
    print(f"Subscribed to topic {receive_topic_hwuid}")
    # Publish calibration timestamp and existing log file
    await client.publish(send_topic_tick, f"Calibration timestamp from {client_name}: {utime.time_ns()}", qos=1)
    print(f"Calibration timestamp from {client_name}: {utime.time_ns()}")
    if log_file_exists:
        await client.publish(send_topic_log, f'{log_content}', qos=1)
        print(f"Published previous log file to topic {send_topic_log}")

async def main(client):
    global timestamps_to_send
    await client.connect()
    print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}")
    while True:
        await asyncio.sleep(1)
        timestamps = timestamps_to_send.copy()
        timestamps_to_send.clear()
        for timestamp in timestamps:
            await client.publish(send_topic_tick, f"{timestamp}", qos=1)
            

# *********************************************
# Connecting to MQTT
# *********************************************

config['server'] = mqtt_broker
config['ssid'] = wifi_name
config['wifi_pw'] = wifi_password
config['subs_cb'] = subscription_callback
config['connect_coro'] = on_connect
client = MQTTClient(config)

# *********************************************
# Reading and publishing timestamps
# *********************************************

latest = 0
count_hall_ticks = 0

# Callback function to record the timestamp of each hall meter pulse
def pulse_callback(pin):
    """
    Callback function to record the timestamp of each hall meter tick 
    and send by mqtt. Sends on topic dist-flow/tick
    """
    global latest
    global count_hall_ticks
    global timestamps_to_send
    
    timestamp = utime.time_ns()
    latest = timestamp
    timestamps_to_send.append(timestamp)

    count_hall_ticks += 1
    if count_hall_ticks > 1000:
        with open('ticks.csv', 'w') as file:
            file.write(f'{timestamp}\n')
        count_hall_ticks = 0

# Set up the pin for input and attach interrupt for rising edge
hall_pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

# *********************************************
# Publishing a Heartbeat
# *********************************************

hb = 0

# Publish a heartbeat, assuming no tick in the last 3 seconds. Acts as a keepalive
async def async_publish_heartbeat(timer):
    global hb
    global latest
    hb = (hb + 1) % 16
    hbstr = "{:x}".format(hb)
    msg =   {'MyHex': hbstr, 'TypeName': 'hb', 'Version': '000'}
    timestamp = utime.time_ns()
    if (timestamp - latest) / 10**9 > HB_FREQUENCY_S:
        await client.publish(send_topic_hb, str(msg), qos=1)
    
def publish_heartbeat(timer):
    loop_heartbeat.create_task(async_publish_heartbeat(timer))

# Create a timer to publish heartbeat every 3 seconds
heartbeat_timer = machine.Timer(-1)
heartbeat_timer.init(period=HB_FREQUENCY_S * 1000, mode=machine.Timer.PERIODIC, callback=publish_heartbeat)
loop_heartbeat.run_forever()

# *********************************************
# Main loop
# *********************************************

try:
    asyncio.run(main(client))
except KeyboardInterrupt:
    print("Program interrupted by user")
    heartbeat_timer.deinit()
finally:
    client.close()