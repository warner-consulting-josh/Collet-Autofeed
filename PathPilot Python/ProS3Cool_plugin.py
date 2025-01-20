# coding=utf-8
from threading import Thread
import time
import glob
import serial
import linuxcnc
from ui_hooks import plugin, StateMachine, StateDescriptor

# Constants
SHORT_SLEEP_TIME = 1.0
LONG_SLEEP_TIME = 1.0
deviceName = "/dev/ProS3"
POWER_OFF_THRESHOLD = 5.0  # Seconds power can be off before pausing execution
TOOL_CHECK_DELAY = 3.0  # Seconds after tool change to check tool number

# Define states
NOT_CONNECTED = 0
CONNECTED_IDLE = 1
TOOL_CHANGED = 2
PROCESSING_RESPONSE = 3

UPDATE_PERIOD = 1.0

class UserPlugin(plugin):
    def __init__(self):
        plugin.__init__(self, 'ProS3Cool with State Machine')

        # Initialize serial object
        self.comPort = serial.Serial()
        self.ShowMsg('comPort created')
        self.last_status_time = time.time()
        self.last_power_on_time = time.time()
        self.last_tool_check_time = None
        self.stat = linuxcnc.stat()
        self.command = linuxcnc.command()
        
        # Track the last tool and microcontroller-reported tool
        self.lastTool = 0
        self.microcontrollerTool = None
        self.power_status = "on"  # Default power status

        # Start the state machine thread
        self.TinyS3Thread = Thread(target=self.UpdateStateMachine)
        self.TinyS3Thread.daemon = True
        self.TinyS3Thread.start()

    def TryToConnect(self):
        devices = glob.glob(deviceName)
        self.ShowMsg('Found devices: %s' % devices)
        if not devices:
            return False

        for symlink in devices:
            try:
                self.comPort.port = symlink
                self.comPort.baudrate = 115200
                self.comPort.timeout = 1
                self.comPort.open()
                self.ShowMsg('Connected to %s' % symlink)
                return True
            except serial.SerialException as e:
                self.ShowMsg('Failed to open %s: %s' % (symlink, str(e)))
        return False

    def UpdateStateMachine(self):
        machine = StateMachine()
        machine.AddState(NOT_CONNECTED, StateDescriptor("Not Connected", self.EnterNotConnected, self.UpdateNotConnected, None))
        machine.AddState(CONNECTED_IDLE, StateDescriptor("Connected Idle", self.EnterConnectedIdle, self.UpdateConnectedIdle, None))
        machine.AddState(TOOL_CHANGED, StateDescriptor("Tool Changed", self.EnterToolChanged, self.UpdateToolChanged, None))
        machine.AddState(PROCESSING_RESPONSE, StateDescriptor("Processing Response", self.EnterProcessingResponse, self.UpdateProcessingResponse, None))
        machine.ChangeState(NOT_CONNECTED)

        while True:
            time.sleep(UPDATE_PERIOD)
            self.halStatus.poll()
            self.read_status_from_microcontroller()
            self.check_errors()
            machine.Update()

    def read_status_from_microcontroller(self):
        if self.comPort.is_open and self.comPort.in_waiting:
            line = self.comPort.readline().decode('utf-8').strip()
            self.process_status_message(line)

    def process_status_message(self, message):
        self.last_status_time = time.time()
        try:
            parts = message.split()
            status_data = {}
            for part in parts:
                key, value = part.split(":")
                status_data[key] = value

            self.microcontrollerTool = int(status_data.get("TOOL", 0))
            self.power_status = status_data.get("PWR", "off")
            pressure_value = int(status_data.get("PRES", 0))

            self.ShowMsg("Received: Tool: %d, Power: %s, Pressure: %d" % (self.microcontrollerTool, self.power_status, pressure_value))
        except Exception as e:
            self.ShowMsg("Error parsing status message: %s" % str(e))

    def check_errors(self):
        self.stat.poll()
        current_time = time.time()
        
        # Check power status first
        if self.stat.task_mode == linuxcnc.MODE_AUTO:
            if self.power_status == "off" and (current_time - self.last_power_on_time > POWER_OFF_THRESHOLD):
                self.ShowMsg("Power has been off for too long! Pausing execution.")
                self.command.abort()
            elif self.power_status == "on":
                self.last_power_on_time = current_time
        
        # Check tool mismatch 2 seconds after tool change
        if self.last_tool_check_time and (current_time - self.last_tool_check_time >= TOOL_CHECK_DELAY):
            if self.microcontrollerTool is not None and self.microcontrollerTool != self.stat.tool_in_spindle:
                self.ShowMsg("Tool mismatch detected! Pausing execution.")
                self.command.abort()
            self.last_tool_check_time = None  # Reset after check

    def EnterNotConnected(self, machine):
        self.ShowMsg("Entering state 'Not Connected'")
        self.comPort.close()

    def UpdateNotConnected(self, machine):
        if self.TryToConnect():
            machine.ChangeState(CONNECTED_IDLE)

    def EnterConnectedIdle(self, machine):
        self.ShowMsg("Entering state 'Connected Idle'")

    def UpdateConnectedIdle(self, machine):
        if not self.comPort.is_open:
            machine.ChangeState(NOT_CONNECTED)
            return

        current_tool = self.halStatus.tool_in_spindle
        if current_tool != self.lastTool:
            self.lastTool = current_tool
            self.last_tool_check_time = time.time()  # Set timer for tool check
            machine.ChangeState(TOOL_CHANGED)

    def EnterToolChanged(self, machine):
        self.ShowMsg("Entering state 'Tool Changed' - Tool %s" % self.lastTool)
        message = "%s\r\n" % self.lastTool
        try:
            self.comPort.write(message.encode('utf8'))
        except serial.SerialException as e:
            self.ShowMsg('Error sending tool data: %s' % str(e))
            machine.ChangeState(NOT_CONNECTED)

    def UpdateToolChanged(self, machine):
        machine.ChangeState(PROCESSING_RESPONSE)

    def EnterProcessingResponse(self, machine):
        self.ShowMsg("Entering state 'Processing Response'")

    def UpdateProcessingResponse(self, machine):
        try:
            response = self.comPort.readline()
            if response:
                self.ShowMsg('Received: %s' % response)
                machine.ChangeState(CONNECTED_IDLE)
        except serial.SerialException as e:
            self.ShowMsg('Error reading from serial port: %s' % str(e))
            machine.ChangeState(NOT_CONNECTED)
