from machine import Pin
import network
import requests
import secrets
from utime import sleep_ms

left_button = Pin(16, Pin.IN, Pin.PULL_UP) # button to turn game on & off
right_button = Pin(28, Pin.IN, Pin.PULL_UP) # button to turn game on & off
forward_button = Pin(27, Pin.IN, Pin.PULL_UP) # button to turn game on & off
reverse_stop_button = Pin(20, Pin.IN, Pin.PULL_UP) # button to turn game on & off

# Used the following Raspberry Pi Article to create the Web Server:
# https://www.raspberrypi.com/news/how-to-run-a-webserver-on-raspberry-pi-pico-w/
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('Waiting for network connection...')
    sleep_ms(1000)

if wlan.status() != 3:
    print(str(wlan.status()) + ' network status.')
    raise RuntimeError('Network connection failed!')
else:
    print('Connected successfully to the network!')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

base_uri = "http://" + secrets.ROBOT_ADDRESS

connected = False
attempts_to_connect = 0
print("Connecting to robot... beep boop")
while connected == False:
    try:
        attempts_to_connect = attempts_to_connect + 1
        response = requests.get(base_uri + "/drive/ping")
        if response.status_code == 200:
            connected = True
            print("Connected to robot! Beep boop!")
    except OSError as e:
        print("Could not connect to robot...")
        if attempts_to_connect > 5:
            raise RuntimeError("Tried connecting to the robot several times and could not! Make sure it is on and try again!")
        else:
            print("Attempting to connect again...")
            sleep_ms(1000)

reverse_button_count = 0
lastCommand = None

while True:
    try:
        if left_button.value() == 0:
            if lastCommand == "left":
                sleep_ms(200)
            print("Left...")
            lastCommand = "left"
            response = requests.get(base_uri + "/drive/left")
            print("Response " + str(response.status_code) + " - " + str(response.content))

        if right_button.value() == 0:
            if lastCommand == "right":
                sleep_ms(200)
            print("Right...")
            lastCommand = "right"
            response = requests.get(base_uri + "/drive/right")
            print("Response " + str(response.status_code) + " - " + str(response.content))

        if forward_button.value() == 0:
            if lastCommand == "forward":
                sleep_ms(200)
            print("Forward...")
            lastCommand = "forward"
            response = requests.get(base_uri + "/drive/forward")
            print("Response " + str(response.status_code) + " - " + str(response.content))

        if reverse_stop_button.value() == 0:
            reverse_button_count = reverse_button_count + 1
            if reverse_button_count > 2:
                if lastCommand == "reverse":
                    sleep_ms(200)
                print("Reverse...")
                lastCommand = "reverse"
                response = requests.get(base_uri + "/drive/reverse")
                print("Response " + str(response.status_code) + " - " + str(response.content))
            else:
                if lastCommand == "stop":
                    sleep_ms(200)
                print("Stop...")
                lastCommand = "stop"
                response = requests.get(base_uri + "/drive/stop")
                print("Response " + str(response.status_code) + " - " + str(response.content))
        else:
            reverse_button_count = 0
    except OSError as e:
        print("Error encountered: " + str(e))

    sleep_ms(100)
