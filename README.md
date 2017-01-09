## What is GarageQTPi

GarageQTPi is basically a server implementation of the Home-Assistant MQTT Cover component for the raspberry pi.
It allows you to run this server on a raspberry pi and add a generic MQTT cover component and control it remotely.

## Motivation

HomeAssistant has integration for raspberry pi garage door openers but only if the instance of home assistant is running on the raspberry pi. If your raspberry pi is soley a garage door opener like mine
then you need to use an MQTT cover component and write code for the raspberry pi.

## Hardware

1. Raspberry pi 3
   CanaKits come with everything you need and definitely the way to go if you aren't sure 
   https://www.amazon.com/CanaKit-Raspberry-Complete-Starter-Kit/dp/B01C6Q2GSY/ref=sr_1_2?s=pc&ie=UTF8&qid=1483671222&sr=1-2&keywords=raspberry+pi
2. Relay
   https://www.amazon.com/gp/product/B0057OC6D8/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1
3. Magnetic switches
   https://www.amazon.com/gp/product/B0009SUF08/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1
4. Additional wires. Used 14 gauge solid copper from relay to garage door and 20 gauge wire for relay switches
5. Mounting Hardware. Can vary depending on how you mount.

Total cost: ~$100. Cheaper if you already have some raspberry pi parts

## Software

## Wiring

![Wiring diagram][1]
Copyright (c) 2013 andrewshilliday

Note: The switches I linked have 3 terminals (COM, NO, NC). You should wire up COM to GND and NO to the GPIO.

## Installation

1. `git clone https://github.com/Jerrkawz/GarageQTPi.git`
2. `pip install -r requirements.txt`
3. edit the configuration.yaml to set up mqtt
4. `python main.py` 
5. Copy this into /etc/rc.local: `(sleep 30; cd /home/pi/GarageQTPi; python main.py)&`
Note: The sleep 30 is my hack to wait until the pi has an ip address so the mqtt connection doesn't fail.
I would like to write this as a daemon eventually and use a real startup service but until then. (or if someone wants to send a PR :) )

## Pictures

## API Reference

The server works with the Home Assisant MQTT Cover component out of the box but if you want to write your own MQTT client you need to adhere to the following API:

Publish one of the following UPPER CASE strings to the command_topic in your config:

OPEN | CLOSE | STOP

Subscribe to the state_topic in your config and you will recieve one of these lower case strings when the state pin changes:

open | closed

Thats it!

## Sample Configuration
```
mqtt:
    host: m10.cloudmqtt.com
    port: *
    user: *
    password: *
doors:
    -
        id: 'left'
        relay: 23
        state: 17
        state_topic: "home-assistant/cover/left"
        command_topic: "home-assistant/cover/left/set"
    -
        id: 'right'
        relay: 24
        state: 18
        state_topic: "home-assistant/cover/right"
        command_topic: "home-assistant/cover/right/set"
```

## Tests

Describe and show how to run the tests with code examples.

## Contributors

I wrote the code myself but as far as hardware/wiring and motivation goes I was heavily insipired by Andrew Shilliday: https://github.com/andrewshilliday/garage-door-controller
Definitely check out his repository if you want a better guide on setting up the hardware.

[1]: http://i.imgur.com/48bpyG0.png