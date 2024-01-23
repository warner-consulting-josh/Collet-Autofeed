# import some python modules
from asyncore import write
from threading import Thread
import time
import glob

# we want access to serial ports
import serial
import io

# definitions of linuxcnc python interfaces
import linuxcnc
import hal

# PathPilot constants
import constants

# base class for plugins
from ui_hooks import plugin

# time(s) between checking the tool number right after it has changed
SHORT_SLEEP_TIME = 1.0

# time(s) between checking the tool number when it hasn't recently changed
LONG_SLEEP_TIME = 1.0

# symlink to the coolant device
deviceName = "/dev/ProS3"

# the plugin class
# one instance is created by ui_hooks.py during system load
# a python Thread (monitorProbe) is used to check the tool number and spindle status
#if the spindle is turned on while tool 99 is loaded, abort() is called

class UserPlugin(plugin):
    # Last tool variable
    lastTool = 0
    def __init__(self):
        # initialise the base class, specifying a name for this plugin
        plugin.__init__(self, 'ProS3Cool')

        # create the serial object - not currently connected
        self.comPort = serial.Serial()
        self.ShowMsg('comPort created')

        # start the worker thread
        self.TinyS3thread = Thread(target=self.ProS3Cool)
        self.TinyS3thread.daemon = True
        self.TinyS3thread.start()

    def TryToConnect(self):
        # look for UDEV names =  /dev/TinyS3
        self.ShowMsg('Trying to connect...')
        
        devices = glob.glob(deviceName)
        self.ShowMsg('Found devices: {}'.format(devices)) # Debugging to check the devices list

        if not devices:
            self.ShowMsg('No devises found matching the pattern')

        for symlink in devices:
            try:
                self.comPort.port = symlink
                self.comPort.baudrate = 115200
                self.comPort.timeout = 1
                self.comPort.open()
                self.ShowMsg('Connected to ' + symlink)
                return True # Return True as soon as connection is successful
            except serial.SerialException as e:
                self.ShowMsg('Failed to open "{}" - {}'.format(symlink, str(e)))
                return False # Return False if no connections were successful
            
        # main loop to watch the current tool and send data to the ProS3
    def ProS3Cool(self):
        self.ShowMsg('ProS3Cool thread is running')

        # Initial serial connection attempt
        if not self.TryToConnect():
            self.ShowMsg('Initial connection attempt failed')
            return # Exit the thread if unable to connect

        while True:
            # make sure hal status info is up to date
            self.halStatus.poll()   
            # check if the serial port is still open, if not try to reconnect
            if self.comPort.is_open:
                self.ShowMsg('Still connected to ProS3')
                # what is the current tool?
                if self.halStatus.tool_in_spindle != self.lastTool:
                    # current tool is a new tool
                    self.lastTool = self.halStatus.tool_in_spindle
                    self.ShowMsg('Current Tool: %s' % (self.halStatus.tool_in_spindle))
                    #self.comPort.write((str(self.halStatus.tool_in_spindle) + '\r\n').encode('utf8'))
                    #time.sleep(SHORT_SLEEP_TIME)
                else:
                    # tool hasn't changed, so sleep for longer before checking again
                    time.sleep(LONG_SLEEP_TIME)

                try:
                    response = self.comPort.readline()
                    if response:
                        self.ShowMsg(response)
                except serial.serialutil.SerialException as e:
                    self.ShowMsg('An error occurred while reading from the serial port: ' + str(e))
                    #serIn = self.comPort.readline()
                    #self.ShowMsg(str(serIn))
            else:
                self.ShowMsg('Connection lost. Trying to reconnect...')
                if not self.TryToConnect():
                    self.ShowMsg('Reconneciton attempt failed')
                    break # Exit the loop if unable to reconnect    
            
            # with a new tool, short sleep before checking again
            time.sleep(SHORT_SLEEP_TIME)
                
            