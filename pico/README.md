# :gift: Setting up a new Pico :gift:

## Installing necessary libraries

Install the `umqtt.simple` package on the Pico:
- Plug in the Pico to a computer
- In Thonny, go to Tools / Manage Packages...
- Search for `umqtt.simple` and install the package

## Finding the Pico's unique identifier

- Save `info.py` (provided in the identification directory) on the Pico
- Either run `info.py` directly on the Pico (in Thonny) or physically connect the Pico to a device and run `get_unique_ids.py` on that device

# Sending messages through MQTT

## 1 - Start a MQTT broker on the Raspberry Pi

One device on the LAN needs to start a MQTT broker.

- Install Mosquitto on the device
- Edit the configuration file `mosquitto.conf`, generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: `mosquitto -c path/to/mosquitto.conf`

## 2 - Connect the Pico to the WiFi and MQTT broker

The code developed in this subsection should be saved as a .py file on the Pico. If you want it to run automatically as soon as the Pico is connected to power, then save it as `main.py`.

### 2.1 - Importing the necessary libraries

```
from umqtt.simple import MQTTClient
import network
import time
```

### 2.2 - Specifying the WiFi and MQTT broker parameters

In the following code:
- Fill in the `wifi_name` and `wifi_password`
- Fill in the `mqtt_broker` (the local IP address of the device on which the MQTT broker is running, in this case the Raspberry Pi), `mqtt_username`, and `mqtt_password` (if there is a username and password)

```
wifi_name = ""
wifi_password = ""

mqtt_broker = ""
mqtt_username = ""
mqtt_password = ""
mqtt_port = 1883

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
client_name = "pico_w"
client = MQTTClient(client_name, mqtt_broker, user=mqtt_username, password=mqtt_password, port=mqtt_port)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}")
```

### 2.3 - Publishing messages on an MQTT topic

Specify the MQTT topic on which you would like the message to be published, and make sure messages are strings.

```
mqtt_topic = b"hall_sensor"
client.publish(mqtt_topic, str(timestamp))
```

# Receiving messages through MQTT

## 