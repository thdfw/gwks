"""
commit ###### of https://github.com/thdfw/gwks/pico/flowmeter/omega_to_mqtt.py
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the omega sensor, on omega_sensor topic
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

node_name = "dist-omega-flow"

# *********************************************
# TOPICS
# *********************************************

send_topic_hb = b"dist-omega-flow/hb"
send_topic_tick = b"dist-omega-flow/tick"
send_topic_hwuid = b"dist-omega-flow/hw-uid-response"
send_topic_log = b"dist-omega-flow/log"

receive_topic_hwuid = b"scada/dist-omega-flow/hw-uid-request"


# *********************************************
# PARAMETERS
# *********************************************


wifi_name = "ARRIS-3007"
wifi_password = "cheat.159.partial"

# Address for beech2 in somerset
mqtt_broker = "192.168.0.175"
mqtt_username = "sara"
mqtt_password = "orca2026"
mqtt_port = 1883

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()
client_name = f"pico_w_{str(pico_unique_id)[-6:]}"
client_live = False
PULSE_PIN = 21

deadband_milliseconds = 100

# *********************************************
# Connecting to WiFi 
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


# *********************************************
# Logging
# *********************************************

def write_in_log(error_message):
    
    # Get human readable time stamp
    ns = utime.time_ns()
    seconds = ns // 1_000_000_000
    microseconds = (ns % 1_000_000_000) // 1_000
    formatted_time = utime.localtime(seconds)
    human_readable = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}.{:03}".format(
        formatted_time[0], formatted_time[1], formatted_time[2],
        formatted_time[3], formatted_time[4], formatted_time[5],
        microseconds
    )
    
    # Print and write to log file
    print(f'{error_message} at time {human_readable}')
    try:
        with open('mqtt.log', 'a') as log_file:
            log_file.write(f'{error_message} at time {human_readable}\n')
            log_file.flush()
    except OSError as e:
        print(f"Error writing to log file ({e})")

# *********************************************
# Connecting to WiFi 
# *********************************************

def connect_mqtt():
    global client_live
    global client
    if client_live == False:
        if client:
            disconnect_mqtt()
        try:
            client = MQTTClient(client_name, mqtt_broker, user=mqtt_username, password=mqtt_password, port=mqtt_port)
            client.connect()
            client.subscribe(receive_topic_hwuid)
            client_live = True
            write_in_log("MQTT client connected")
        except Exception as e:
            write_in_log(f"Failed to connect to MQTT broker: {e}")
            client_live = False
    else:
        print("Not trying to reconnect")


def disconnect_mqtt():
    global client
    try:
        if client:
            client.disconnect()  # Gracefully disconnect from the broker
            print("MQTT client disconnected")
    except Exception as e:
        write_in_log(f"Error while disconnecting MQTT client: {e}")
    finally:
        client = None  # Ensure the client object is cleared

# Publish a first timestamp
connect_mqtt()
client.publish(send_topic_tick, f"Calibration timestamp from {client_name}: {utime.time_ns()}")

# Publish the content of the previous log file
if log_file_exists:
    client.publish(send_topic_log, f'{log_content}')
    print(f"Published previous log file to topic {send_topic_log}")

# *********************************************
# Reading timestamps
# *********************************************

latest = 0

def pulse_callback(pin):
    """
    Callback function to record the timestamp of each omega meter pulse
    Ignore false positives in jitter happening under deadband milliseconds
    (e.g. 100 ms) as even an ekm meter with 0.0748 gpm will have at least a
    500 ms period at 10 gpm
    """
    global latest
    global client_live
    timestamp = utime.time_ns()
    if timestamp - latest > 1_000_000 * deadband_milliseconds:
        latest = timestamp
        if client_live:
            try:
                client.publish(send_topic_tick , f"{timestamp}")
            except Exception as e:
                print(f"Failed to publish: {e}")
                client_live = False

# Set up the pin for input and attach interrupt for falling edge
pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
pulse_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=pulse_callback)

# *********************************************
# Publish Heartbeat
# *********************************************
hb = 0

def publish_heartbeat(timer):
    """
    Publish a heartbeat, assuming no omega tick in the last 5 minutes.
    Acts as a keepalive
    """
    global hb
    global latest
    hb = (hb + 1) % 16
    hbstr = "{:x}".format(hb)
    msg =  {'MyHex': hbstr, 'TypeName': 'hb', 'Version': '000'}
    timestamp = utime.time_ns()
    if (timestamp - latest) / 10**9 > 300:
        if client_live:
            try:
                client.publish(send_topic_hb, str(msg))
            except Exception as e:
                print(f"Failed to publish hb: {e}")
                client_live = False


# Create a timer to publish heartbeat every 3 seconds
heartbeat_timer = machine.Timer(-1)
heartbeat_timer.init(period=3000, mode=machine.Timer.PERIODIC, callback=publish_heartbeat)


try:
    while True:
        if not client_live:
            connect_mqtt()
        utime.sleep(5)
except KeyboardInterrupt:
    print("Program interrupted by user")