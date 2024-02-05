import board
import neopixel
import time
import supervisor
import sys
import microcontroller
from watchdog import WatchDogMode, WatchDogTimeout

# Initialize NeoPixel LED
pix = neopixel.NeoPixel(board.NEOPIXEL, 1)
pix.fill((0, 0, 0))  # LED off initially
serial = sys.stdin
oldData = None
led_on_time = 0
blink_duration = 0.5

# Prepare Watchdog but don't start it yet
watchdog = microcontroller.watchdog
watchdog.timeout = 45  # Set a suitable timeout
watchdog.mode = WatchDogMode.RESET
watchdog_started = False

# Check the reset reason
print(microcontroller.cpu.reset_reason)

while True:
    if supervisor.runtime.serial_bytes_available:
        dataIn = serial.readline().strip()  # Read and strip the incoming data

        # Check if the incoming data is the specific string to start the watchdog
        if dataIn == "ProS3" and not watchdog_started:
            watchdog.feed()  # Start feeding the watchdog to keep it from resetting the board
            watchdog_started = True
            print(microcontroller.cpu.reset_reason)
            print("Watchdog timer started.")
            continue  # Skip the rest of the loop after starting the watchdog

        # Process other data as before
        try:
            if watchdog_started:  # Only process numbers if the watchdog has been started
                dataInt = int(dataIn)
                if dataInt != oldData:
                    oldData = dataInt
                    pix.fill((0, 100, 0))  # Turn on LED
                    led_on_time = time.monotonic()  # Record the time LED was turned on
                    print('ProS3 sees tool:' + str(dataInt))
                    watchdog.feed()
        except ValueError:
            print("Received non-integer data")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    current_time = time.monotonic()

    # Implement non-blocking LED turn-off
    if current_time - led_on_time >= blink_duration and pix[0] != (0, 0, 0):
        pix.fill((0, 0, 0))  # Turn off LED

    # Continue feeding the watchdog if it has been started
    #if watchdog_started:
        #watchdog.feed()
