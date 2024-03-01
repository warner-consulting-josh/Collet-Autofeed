import board
import neopixel
import time
import supervisor
import sys
import digitalio
import microcontroller
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# Initialize NeoPixel LED
pix = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
pix.fill((0, 0, 0))

# Initialize OLED screen and draw a white border
displayio.release_displays() # releases any old displays so that the new one can be created

oled_reset = board.D7

i2c = board.I2C()  # uses board.SCL and board.SDA
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D, reset=oled_reset)  # Adjusted address to 0x3D

WIDTH = 128
HEIGHT = 64
BORDER = 1

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
splash.append(inner_sprite)

# Add Tool Number Label
ToolNumberLabelArea = label.Label(terminalio.FONT, text=" "*20, color=0xFFFFFF)
ToolNumberLabelArea.anchor_point = (0.0, 0.0)
ToolNumberLabelArea.anchored_position = (2, 1)
splash.append(ToolNumberLabelArea)

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
blink_duration = 2.0

print(microcontroller.cpu.reset_reason)

while True:
    current_time = time.monotonic()

    # Implement non-blocking LED blink-off logic
    if led_on_time is not None and current_time - led_on_time >= blink_duration:
        pix.fill((0, 0, 0))
        pix.show()
        led_on_time = None

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

                print(f'Tool Number: {dataInt}')
                ToolNumberLabelArea.text = f'Tool Number: {dataInt}'
        except ValueError:
            print("Received non-integer data")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

