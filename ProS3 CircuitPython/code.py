import board
import digitalio
import neopixel
import time
import supervisor
import sys

# Assuming NEOPIXEL is available
pix = neopixel.NeoPixel(board.NEOPIXEL, 1)
pix.fill((0, 0, 0))  # Initialize with the LED off
serial = sys.stdin
oldData = None

while True:
    if supervisor.runtime.serial_bytes_available:
        dataIn = ''
        char = serial.read(1)  # Read one character at a time
        while char != '\n' and char:  # Continue until newline or empty string (indicating no more data)
            if char.isdigit() or char in ['-', '\r']:  # Accept digits and negative sign
                dataIn += char
            char = serial.read(1)
        dataIn = dataIn.strip()

        try:
            dataInt = int(dataIn)
            if dataInt != oldData:
                oldData = dataInt  # Update oldData to the new value
                pix.fill((0, 100, 0))  # Change color to green
                time.sleep(0.5)  # Wait for half a second
                pix.fill((0, 0, 0))  # Turn off the LED
                print('ProS3 sees tool:' + str(dataInt))
        except ValueError:
            print(f"Received non-integer data")
        except Exception as e:  # General exception handler for anything unexpected
            print(f"An unexpected error occurred: {e}")
        except UnicodeError:
            # Handle cases where there's a Unicode-related error
            print("Received data with invalid Unicode characters.")
