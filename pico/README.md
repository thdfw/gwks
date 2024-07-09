# :gift: Setting up a new Pico

## Installing necessary libraries

Install the `umqtt.simple` package on the Pico:
- Plug in the Pico to a computer
- In Thonny, go to Tools / Manage Packages...
- Search for `umqtt.simple` and install the package

## Finding the Pico's unique identifier

In `identifcation/`, the `info.py` and `get_unique_ids.py` codes are provided. Save `info.py` on the Pico.
- Either run `info.py` directly on the Pico (in Thonny)
- Or physically connect the Pico to a device and run `get_unique_ids.py` on that device

# :outbox_tray: Sending messages through MQTT (Pico -> Raspberry Pi) 

## 1 - Start a MQTT broker on the Raspberry Pi

- If necessary, install Mosquitto on the device
- Edit the configuration file `mosquitto.conf`, generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: `mosquitto -c path/to/mosquitto.conf`

## 2 - Connect the Pico to the WiFi and MQTT broker

In any code which is destined for the Pico to be sending MQTT messages, the following three steps apply. The code below is an example, it publishes a message on a given MQTT topic every 10 seconds.
- Save the code as a .py file on the Pico. If you want it to run automatically as soon as the Pico is connected to power, then save it as `main.py`.
- Fill in the parameters: `wifi_name`, `wifi_password`, `mqtt_broker` (the local IP address of the device on which the MQTT broker is running, i.e. the Raspberry Pi), `mqtt_username`, and `mqtt_password` (if there is a username and password)
- Specify the MQTT topic on which you would like the message to be published (`mqtt_topic`) and client name (`client_name`)

```
from umqtt.simple import MQTTClient
import network
import time

# Fill in these parameters
wifi_name = ""
wifi_password = ""
mqtt_broker = ""
mqtt_username = ""
mqtt_password = ""
mqtt_port = 1883

# Specify the client name and topic
client_name = "pico_w"
mqtt_topic = b"hall_sensor"

# Connect to WiFi
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

# Publish a messsage every 10 seconds
counter = 0
while(1):
    client.publish(mqtt_topic, str(counter))
    counter += 1
    time.sleep(10)

```

# :inbox_tray: Receiving the Pico's messages sent through MQTT

## 


mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "hall_sensor"

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribes to the given MQTT topic'''
    print(f"Connected and subscribed to {mqtt_topic}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    '''This function is called at every received message'''
    data = message.payload.decode()
    print(f"Received data: {data}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()