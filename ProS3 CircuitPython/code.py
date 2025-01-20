import board
import neopixel
import time
import supervisor
import sys
import digitalio
import analogio
import microcontroller
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# Initialize NeoPixel LED
pix = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
pix.fill((0, 0, 0))

# Initialize OLED screen and draw a white border
displayio.release_displays()
oled_reset = board.D7

i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D, reset=oled_reset)
WIDTH = 128
HEIGHT = 64
BORDER = 1

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
splash.append(inner_sprite)

ToolNumberLabelArea = label.Label(terminalio.FONT, text=" " * 20, color=0xFFFFFF, scale=2)
ToolNumberLabelArea.anchor_point = (0.0, 0.0)
ToolNumberLabelArea.anchored_position = (2, 1)
splash.append(ToolNumberLabelArea)

PwrLabelArea = label.Label(terminalio.FONT, text=" " * 20, color=0xFFFFFF, scale=2)
PwrLabelArea.anchor_point = (0.0, 1)
PwrLabelArea.anchored_position = (2, 65)
splash.append(PwrLabelArea)

PresLabelArea = label.Label(terminalio.FONT, text=" " * 20, color=0xFFFFFF, scale=2)
PresLabelArea.anchor_point = (0.0, 0.5)
PresLabelArea.anchored_position = (2, 32)
splash.append(PresLabelArea)

pin_mappings = [
    (1, board.IO16),
    (2, board.IO0),
    (3, board.IO21),
    (4, board.IO5),
    (5, board.IO4),
    (6, board.IO3),
    (7, board.IO2),
    (8, board.IO1)
]

output_pins = {}
for number, pin_id in pin_mappings:
    pin = digitalio.DigitalInOut(pin_id)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = True  # Active low logic
    output_pins[number] = pin

pwr_pin = board.IO12
pwr_monitor = digitalio.DigitalInOut(pwr_pin)
pwr_monitor.direction = digitalio.Direction.INPUT
pwr_monitor.pull = digitalio.Pull.DOWN

pres_pin = board.IO13
pres_input = analogio.AnalogIn(pres_pin)

serial = sys.stdin
sys.stdout = sys.stdout  # Ensure stdout is set up for output

class StateMachine:
    def __init__(self):
        self.state = "IDLE"
        self.led_on_time = None
        self.oldData = None
        self.pwr_check_start = time.monotonic()
        self.pres_check_start = time.monotonic()
        self.status_report_time = time.monotonic()

    def update(self):
        current_time = time.monotonic()

        if self.state == "IDLE":
            self.check_power(current_time)
            self.check_pressure(current_time)
            self.read_serial(current_time)
            self.report_status(current_time)

        elif self.state == "PROCESS_SERIAL":
            self.process_serial_data()

        elif self.state == "BLINK_LED":
            self.blink_led(current_time)

    def check_power(self, current_time):
        if current_time - self.pwr_check_start >= 0.5:
            pwr_state = pwr_monitor.value
            pwr_text = "on" if pwr_state else "off"
            PwrLabelArea.text = 'Power: %s' % pwr_text
            self.pwr_check_start = current_time

    def check_pressure(self, current_time):
        if current_time - self.pres_check_start >= 0.5:
            pres_val = pres_input.value
            PresLabelArea.text = 'Pres: %d' % pres_val
            self.pres_check_start = current_time

    def read_serial(self, current_time):
        if supervisor.runtime.serial_bytes_available:
            data_in = serial.readline().strip()
            try:
                data_int = int(data_in)
                if data_int != self.oldData:
                    self.oldData = data_int
                    self.state = "PROCESS_SERIAL"
            except ValueError:
                print("Non-integer data")

    def report_status(self, current_time):
        if current_time - self.status_report_time >= 1.0:
            pwr_status = "on" if pwr_monitor.value else "off"
            pres_val = pres_input.value
            print('TOOL:%d PWR:%s PRES:%d' % (self.oldData if self.oldData else 0, pwr_status, pres_val))
            self.status_report_time = current_time

    def process_serial_data(self):
        if self.oldData is not None:
            ToolNumberLabelArea.text = 'Tool: %d' % self.oldData
            #print('%d' % self.oldData)  # Send tool number back over serial

            for pin in output_pins.values():
                pin.value = True

            if self.oldData in output_pins:
                output_pins[self.oldData].value = False

            pix.fill((0, 100, 0))
            pix.show()
            self.led_on_time = time.monotonic()
            self.state = "BLINK_LED"

    def blink_led(self, current_time):
        if self.led_on_time is not None and current_time - self.led_on_time >= 2.0:
            pix.fill((0, 0, 0))
            pix.show()
            self.led_on_time = None
            self.state = "IDLE"

state_machine = StateMachine()

print(microcontroller.cpu.reset_reason)

while True:
    state_machine.update()
    time.sleep(0.01)  # Prevent high CPU usage
