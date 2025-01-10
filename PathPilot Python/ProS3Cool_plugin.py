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

        # Track the last tool
        self.lastTool = 0

        # Start the state machine thread
        self.TinyS3Thread = Thread(target=self.UpdateStateMachine)
        self.TinyS3Thread.daemon = True
        self.TinyS3Thread.start()

    def TryToConnect(self):
        devices = glob.glob(deviceName)
        self.ShowMsg(f'Found devices: {devices}')
        if not devices:
            return False

        for symlink in devices:
            try:
                self.comPort.port = symlink
                self.comPort.baudrate = 115200
                self.comPort.timeout = 1
                self.comPort.open()
                self.ShowMsg(f'Connected to {symlink}')
                return True
            except serial.SerialException as e:
                self.ShowMsg(f'Failed to open {symlink}: {e}')
        return False

    def UpdateStateMachine(self):
        # Create the state machine
        machine = StateMachine()

        # Add states
        machine.AddState(NOT_CONNECTED, StateDescriptor("Not Connected", self.EnterNotConnected, self.UpdateNotConnected, None))
        machine.AddState(CONNECTED_IDLE, StateDescriptor("Connected Idle", self.EnterConnectedIdle, self.UpdateConnectedIdle, None))
        machine.AddState(TOOL_CHANGED, StateDescriptor("Tool Changed", self.EnterToolChanged, self.UpdateToolChanged, None))
        machine.AddState(PROCESSING_RESPONSE, StateDescriptor("Processing Response", self.EnterProcessingResponse, self.UpdateProcessingResponse, None))

        # Start in the NOT_CONNECTED state
        machine.ChangeState(NOT_CONNECTED)

        while True:
            time.sleep(UPDATE_PERIOD)
            self.halStatus.poll()  # Ensure HAL status is up-to-date
            machine.Update()

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
            machine.ChangeState(TOOL_CHANGED)

    def EnterToolChanged(self, machine):
        self.ShowMsg(f"Entering state 'Tool Changed' - Tool {self.lastTool}")
        message = f"{self.lastTool}\r\n".encode('utf8')
        try:
            self.comPort.write(message)
        except serial.SerialException as e:
            self.ShowMsg(f'Error sending tool data: {e}')
            machine.ChangeState(NOT_CONNECTED)

    def UpdateToolChanged(self, machine):
        machine.ChangeState(PROCESSING_RESPONSE)

    def EnterProcessingResponse(self, machine):
        self.ShowMsg("Entering state 'Processing Response'")

    def UpdateProcessingResponse(self, machine):
        try:
            response = self.comPort.readline()
            if response:
                self.ShowMsg(f'Received: {response}')
                machine.ChangeState(CONNECTED_IDLE)
        except serial.SerialException as e:
            self.ShowMsg(f'Error reading from serial port: {e}')
            machine.ChangeState(NOT_CONNECTED)
