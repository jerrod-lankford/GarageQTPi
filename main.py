#!/usr/bin/python3
import json
import logging
import random
import re
import threading

import paho.mqtt.client as mqtt
import paho.mqtt


from lib.garage import GarageDoor
from lib.garage import TwoSwitchGarageDoor
from config import Config


print("GarageQTPi starting")
discovery_info = {}
garage_doors = []
config = Config()
config.read()
config.validate()

# Update the mqtt state topic

def poll(door, topic):
    """ Polls door state after a door command is issued """
    value = door.state
    logging.info("Door has been polled. State is -> %s" % (value))


def update_state(value, topic):
    logging.info("State change triggered: %s -> %s" % (topic, value))

    client.publish(topic, value, retain=True)

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code: %s" % mqtt.connack_string(rc))
    # notify subscribed clients that we are available
    client.publish(userdata["config"].get_item("mqtt","availability_topic"), userdata["config"].get_item("mqtt","payload_available"), retain=True)

    logging.info(
        "Sent payload: '" +
        userdata["config"].get_item('mqtt','payload_available') +
        "' to topic: '" +
        userdata["config"].get_item('mqtt','availability_topic') +
        "'")

    for config in userdata["config"].get_section('doors'):
        command_topic = config['command_topic']
        logging.info("Listening for commands on %s" % command_topic)
        client.subscribe(command_topic)

    # Update each door state in case it changed while disconnected.
    for door in userdata["doors"]:
        client.publish(door.state_topic, door.state, retain=True)

# Execute the specified command for a door


def execute_command(door, command):
    try:
        doorName = door.name
    except BaseException:
        doorName = door.id
    logging.info("Executing command %s for door %s" % (command, doorName))
    if door.poll_delay > 0:
        logging.info("Starting polling thread.")
        # Set up a timer thread for polling the door
        poller[doorCfg['name']] = threading.Timer(door.poll_delay, poll, [door, command_topic])
        poller[doorName].start()

    if command == "OPEN" and door.state == 'closed':
        door.open()
    elif command == "CLOSE" and door.state == 'open':
        door.close()
    elif command == "STOP":
        door.stop()
    else:
        logging.info("Invalid command: %s" % command)

#
# setup logging and then log sucessful configuration validation
#
if config.get_item('logging','show_timestamp'):
    logging.basicConfig(format='%(asctime)s %(message)s',level=config.get_item("logging","log_level"))
else:
    logging.basicConfig(level=config.get_item("logging","log_level"))

logging.info ("Config sucessfully validated against schema")
logging.info (json.dumps(config.all, indent = 4))

### SETUP MQTT ###
user = config.get_item('mqtt','user')
password = config.get_item('mqtt','password')
host = config.get_item('mqtt','host')
port = int(config.get_item('mqtt','port'))
discovery = config.get_item('mqtt', 'discovery')
discovery_prefix=config.get_item('mqtt','discovery_prefix')
availability_topic = config.get_item('mqtt','availability_topic')    
payload_available = config.get_item('mqtt','payload_available')
payload_not_available = config.get_item('mqtt','payload_not_available')
userdata={}
userdata["config"] = config
userdata["doors"] = garage_doors

client = mqtt.Client(client_id="MQTTGarageDoor_{:6s}".format(str(random.randint(
    0, 999999))), clean_session=True, userdata=userdata, protocol=mqtt.MQTTv311)

client.on_connect = on_connect

client.username_pw_set(user, password=password)

# set a last will message so the broker will notify connected clients when
# we are not available
client.will_set(availability_topic, payload_not_available, retain=True)
logging.info(
    "Set last will message: '" +
    payload_not_available +
    "' for topic: '" +
    availability_topic +
    "'")

# Dictionary to store polling threads
poller = {}

client.connect(host, port, 60)


# Create door objects and create callback functions
for doorCfg in config.get_section('doors'):

    # If no name it set, then set to id
    if 'name' not in doorCfg or doorCfg['name'] is None:
        doorCfg['name'] = doorCfg['id']
    
    # Sanitize id value for mqtt
    doorCfg['id'] = re.sub(r'\W+', '', re.sub(r'\s', ' ', doorCfg['id']))

    if discovery is True:
        base_topic = discovery_prefix + "/cover/" + doorCfg['id']
        config_topic = base_topic + "/config"
        doorCfg['command_topic'] = base_topic + "/set"
        doorCfg['state_topic'] = base_topic + "/state"

    command_topic = doorCfg['command_topic']
    state_topic = doorCfg['state_topic']
    poll_delay = doorCfg['poll_delay']


    #
    # If the open switch is specified use a two switch garage door
    # otherwise use a door with only a closed switch.
    # The interface is the same.  The two switch garage door
    # reports the states "open" and "closed"
    #
    if "open" in doorCfg and doorCfg["open"] is not None:
        door = TwoSwitchGarageDoor(doorCfg)
    else:
        door = GarageDoor(doorCfg)



    # Callback per door that passes a reference to the door
    def on_message(client, userdata, msg, door=door):
        execute_command(door, msg.payload.decode("utf-8"))

    # Callback per door that passes the doors state topic
    def on_state_change(value, topic=state_topic):
        update_state(value, topic)

    client.message_callback_add(command_topic, on_message)

    # You can add additional listeners here and they will all be executed
    # when the door state changes
    door.onStateChange.addHandler(on_state_change)

    # Publish initial door state
    client.publish(state_topic, door.state, retain=True)

    # Store Garage Door instance for use on reconnect
    door.state_topic = state_topic
    door.command_topic = command_topic
    garage_doors.append(door)


    # If discovery is enabled publish configuration
    if discovery is True:

        discovery_info["name"] = doorCfg['name']
        discovery_info["command_topic"] = doorCfg['command_topic']
        discovery_info["state_topic"] = doorCfg['state_topic']
        discovery_info["availability_topic"] = availability_topic
        discovery_info["payload_available"] = payload_available
        discovery_info["payload_not_available"] = payload_not_available
        discovery_info["unique_id"] = doorCfg['uuid']
        client.publish(
            config_topic,
            json.dumps(discovery_info),
            retain=True)

        logging.info(
            "Sent audodiscovery config: " +
            json.dumps(
                discovery_info,
                indent=4))
        logging.info("to topic: " + config_topic)

# Main loop
if __name__ == "__main__":
    client.loop_forever()
