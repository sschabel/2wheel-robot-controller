import asyncio

import aioble
from machine import Pin
import bluetooth
from utime import sleep_ms

# NUS UUIDs
_UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
_UART_TX_UUID = bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
_UART_RX_UUID = bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')

peripheral_name = "RCCar"

async def find_rc_car():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == peripheral_name and _UART_UUID in result.services():
                return result.device
    return None

left_button = Pin(16, Pin.IN, Pin.PULL_UP) # button to turn game on & off
right_button = Pin(28, Pin.IN, Pin.PULL_UP) # button to turn game on & off
forward_button = Pin(27, Pin.IN, Pin.PULL_UP) # button to turn game on & off
reverse_stop_button = Pin(20, Pin.IN, Pin.PULL_UP) # button to turn game on & off

reverse_button_count = 0
lastCommand = None

async def main():
    while True:
        device = await find_rc_car()
        if not device:
            print("RC Car not found. Retrying...")
            await asyncio.sleep_ms(2000)  # Wait before retrying
            continue

        try:
            print("Connecting to", device)
            connection = await device.connect()
        except asyncio.TimeoutError:
            print("Connection timeout")
            continue

        async with connection:
            try:
                uart_service = await connection.service(_UART_UUID)
                rx_characteristic = await uart_service.characteristic(_UART_RX_UUID)
            except Exception:
                print("Failed to find service/characteristic")
                continue

            print("Ready to send commands. Enter: forward, reverse, left, right, stop, or exit")

            cmd = None
            while True:
                if left_button.value() == 0:
                    cmd = 'left'
                    lastCommand = cmd
                if right_button.value() == 0:
                    cmd = 'right'
                    lastCommand = cmd
                if forward_button.value() == 0:
                    cmd = 'forward'
                    lastCommand = cmd
                if reverse_stop_button.value() == 0:
                    reverse_button_count = reverse_button_count + 1
                    if reverse_button_count > 2:
                        if lastCommand == "reverse":
                            sleep_ms(200)
                        print("Reverse...")
                        cmd = 'reverse'
                    else:
                        if lastCommand == "stop":
                            sleep_ms(200)
                        cmd = 'stop'
                else:
                    reverse_button_count = 0
                if cmd is not None:
                    await rx_characteristic.write(cmd.encode('utf-8'))
                    print("Sent: ", cmd)
                    cmd = None
                sleep_ms(100)

asyncio.run(main())
