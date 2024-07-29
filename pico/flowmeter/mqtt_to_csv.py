"""
This code is designed to run on a Pi. It reads MQTT messages on the topics 'hall_sensor' 
and 'ekm_sensor' and saves them as timestamped rows in a CSV file in /home/pi/mqtt_files/

Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run pico_to_mqtt.py on the Pico W (either call it main.py or through Thonny)
- Run this code to save the data to CSV files live
"""

import time
import threading
import csv
import pendulum
import paho.mqtt.client as mqtt

#
# IMPORTANT: decide wether or not you want the watchdog to be active
#
WATCHDOG = True

# *********************************************
# PARAMETERS
# *********************************************
directory = '/home/pi/mqtt_files/'
mqtt_broker = "localhost"
mqtt_port = 1883
hall_tick_topic = "dist-flow/tick"
omega_tick_topic = "dist-omega-flow/tick"

hall_hb_topic = "dist-flow/hb"
omega_hb_topic = "dist-omega-flow/hb"

hall_log_topic = "dist-flow/log"
omega_log_topic = "dist-omega-flow/log"

last_message_time = time.time()


# *********************************************
# Writing received MQTT messages to a CSV file
# *********************************************

now_for_file = pendulum.now('America/New_York').format('YYYY-MM-DD_HH-mm-ss')

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribes to the MQTT topics'''
    client.subscribe(hall_tick_topic)
    print(f"Connected and subscribed to {hall_tick_topic}")
    client.subscribe(omega_tick_topic)
    print(f"Connected and subscribed to {omega_tick_topic}")
    client.subscribe(hall_hb_topic)
    print(f"Connected and subscribed to {hall_hb_topic}")
    client.subscribe(omega_hb_topic)
    print(f"Connected and subscribed to {omega_hb_topic}")
    client.subscribe(hall_log_topic)
    print(f"Connected and subscribed to {hall_log_topic}")
    client.subscribe(omega_log_topic)
    print(f"Connected and subscribed to {omega_log_topic}")
    csv_file = directory + f"hall/omega_{now_for_file}.csv"
    print(f"Writing to {csv_file}. Using America/New Timezone")


def on_message(client, userdata, message):
    '''Writes the data received on the MQTT topics to distinct CSV files'''
    global last_message_time
    last_message_time = time.time()
    data = message.payload.decode()
    topic = message.topic
    if topic == hall_log_topic:
        log_file = directory + f"dist-flow.log"
        with open(log_file, mode='a') as file:
            file.write(str(data))
    elif topic == omega_log_topic:
        log_file = directory + f"dist-omega-flow.log"
        with open(log_file, mode='a') as file:
            file.write(str(data))
    if topic not in [hall_tick_topic, omega_tick_topic]:
        return
    if 'Calibration' in data:
        print(data)
        return
    try:
        data = int(data)
    except ValueError:
        print(f"Warning: Non-integer data received on topic {topic}: {data}")
        return
    if topic == hall_tick_topic:
        csv_file = directory + f"hall_{now_for_file}.csv"
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), int(data)])
    elif topic == omega_tick_topic:
        csv_file = directory + f"omega_{now_for_file}.csv"
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), int(data)])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

if WATCHDOG:
        
    from gwproto.enums import ChangeAquastatControl, ChangeHeatPumpControl, ChangeRelayState
    from nsm_base import NSMBase
    from typing import Dict
    from actors.config import GeorgeScratchSettings as Settings
    from data_classes.house_0_layout import RelayActionChoice
    from data_classes.house_0_layout import House0RelayIdx as RelayIdx
    import dotenv
    import krida

    class PowerCycle(NSMBase):

        def __init__(self, settings: Settings, relays: Dict[int, RelayActionChoice]):
            super().__init__(settings, relays)

        def enter_onpeak_event(self):
            pass

        def enter_offpeak_event(self):
            pass

        def cycle_picos(self):
            print("Started cycling")
            self.start_driver()
            time.sleep(5)
            self.change_relay_state(self.relays[RelayIdx.PICOS], ChangeRelayState.OpenRelay)
            time.sleep(10)
            self.change_relay_state(self.relays[RelayIdx.PICOS], ChangeRelayState.CloseRelay)
            time.sleep(10)
            print("Finished cycling")

    nsm = PowerCycle(settings=Settings(_env_file=dotenv.find_dotenv()), relays=krida.RELAYS)

    def check_last_message():
        '''Thread function to check the time since the last received message'''
        global last_message_time
        while True:
            time.sleep(5)
            if time.time() - last_message_time > 10:
                time_str = pendulum.now('America/New_York').format('HH:mm:ss')
                print(f"[{time_str}] Warning: No message received in the last 10 seconds")
                nsm.cycle_picos()

# Create and start the thread for checking the last message time
warning_thread = threading.Thread(target=check_last_message)
warning_thread.daemon = True
warning_thread.start()


client.loop_forever()