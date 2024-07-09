# Finding a Pico's unique identifier

- Save `info.py` (provided in the identification directory) on the Pico
- Physically connect the Pico to a device
- Run `get_unique_ids.py` on that device, and read prints

# Sending messages through MQTT

## Start a MQTT broker on the Raspberry Pi

One device on the LAN needs to start a MQTT broker.

- Install Mosquitto on the device
- Edit the configuration file `mosquitto.conf`, generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: `mosquitto -c path/to/mosquitto.conf`

## Connecting the Pico to the WiFi and MQTT broker

In the `pico_to_mqtt.py` file:
- Edit the `wifi_name` and `wifi_password`
- Edit the `mqtt_broker`, `mqtt_username`, and `mqtt_password` (the `mqtt_broker` should be the local IP address of the device on which the MQTT broker is running, in this case the Raspberry Pi.)

```
wifi_name = ""
wifi_password = ""

mqtt_broker = ""
mqtt_username = ""
mqtt_password = ""

mqtt_port = 1883
mqtt_topic = b"hall_sensor"

client_name = "pico_w"

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
```