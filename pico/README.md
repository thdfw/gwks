# Finding a Pico's unique identifier

- Save 'info.py' (provided in the identification directory) on the Pico
- Physically connect the Pico to a device
- Run 'get_unique_ids.py' on that device, and read prints

# Sending messages through MQTT

## Start a MQTT broker on the Raspberry Pi

One device on the LAN needs to start a MQTT broker.

- Install Mosquitto on the device
- Edit the configuration file 'mosquitto.conf', generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: 'mosquitto -c path/to/mosquitto.conf'

## 