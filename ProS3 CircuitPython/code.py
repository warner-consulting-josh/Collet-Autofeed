import board
import neopixel
import time
import supervisor
import sys
import digitalio
import microcontroller

# Initialize NeoPixel LED
pix = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
pix.fill((0, 0, 0))

# List of tuples correlating serial number inputs to GPIO pins
pin_mappings = [
    (5, board.IO43),  # Example: (serial_number, GPIO_pin)
    # Add more mappings here as needed
]

# Create and initialize GPIO pins based on the mappings
output_pins = {}
for number, pin_id in pin_mappings:
    pin = digitalio.DigitalInOut(pin_id)
    pin.direction = digitalio.Direction.OUTPUT
    # Pins are in push-pull mode by default when configured as digital outputs
    pin.value = True  # Set high (inactive) for active low logic
    output_pins[number] = pin
    
serial = sys.stdin
oldData = None
led_on_time = None
blink_duration = 0.5

print(microcontroller.cpu.reset_reason)

while True:
    current_time = time.monotonic()
    
    # Implement non-blocking LED blink-off logic
    if led_on_time is not None and current_time - led_on_time >= blink_duration:
        pix.fill((0, 0, 0))
        pix.show()
        #led_on_time = None

    if supervisor.runtime.serial_bytes_available:
        dataIn = serial.readline().strip()  # Read and strip the incoming data

        try:
            dataInt = int(dataIn)
            if dataInt != oldData:
                oldData = dataInt
                # Blink the LED
                pix.fill((0, 100, 0))
                pix.show()
                led_on_time = current_time
                
                # Turn off all GPIO pins initially
                for pin in output_pins.values():
                    pin.value = True  # Set high (inactive)

                # Then, if the number is in the mappings, turn on the corresponding GPIO pin
                if dataInt in output_pins:
                    output_pins[dataInt].value = False  # Active low logic
                
                print(f'Activated by serial number: {dataInt}')
        except ValueError:
            print("Received non-integer data")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
