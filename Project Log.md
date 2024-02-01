# Project Log
Notes on what I did each day so that I can keep track of my changes and remember where/what I was working on

**01/22/2024**
- Installed Mu and plugged in TinyS3 Pro
  - Defualt code running
- Downloaded latest ui_hooks.py and installed into OLD PathPilot VM
- Commented out lines in ~/tmc/python/pathpilotmanager.py so that I don't have to pick configuration of machine every time
```
# state of the VM leftover from a previous student.
#            if os.path.exists(PATHPILOTJSON_FILE):
#                os.unlink(PATHPILOTJSON_FILE)
#                print "Removing config file to force selection of machine type in sim mode."
```
- Installed ToolPrint_plugin.py on OLD Pathpilot VM and verified it is working

**01/23/2024**
- Added "UnexpectedMaker ProS3 [0100]" to USB Device filter with USB 3.0 Controller enabled
  - CIRCUITPY drive shows up in Linux
- Added 99-ProS3.rules to /etc/udev/rules.d
```
ACTION=="add",SUBSYSTEMS=="usb",KERNEL=="ttyACM*",ATTRS{manufacturer}=="UnexpectedMaker",ATTRS{product}=="ProS3",SYMLINK+="ProS3",GROUP="dialout",MODE="0666"
```
- Modified TinyS3io.py to ProS3Cool.py and tryed to get a serial connection working
  - Plugin runs but does not successfully invoke TryToConnect()
  - Need to look into syntax and figure out why it isn't calling the function
**01/23/2024 update**
- Successfully invoked TryToConnect()
  - Previously: `self.ComPor.TryToConnect()`
  - Corrected: `self.TryToConnect()`
- Added some debug and error prevention to ProS3_plugin.py

**01/24/2024**
- Worked on getting the ProS3 to respond to data sent by the ProS3Cool plugin
- Got the microcontroller to respond to serial data sent using Mu
- Currently getting a unicode? error that causes the ProS3 to exit it's code loop and enter the REPL

**01/25/2024**
- Successfully established 2 way serial communication between the ProS3_plugin.py code and the ProS3 microcontroller
  - Needed to disable modemmanager in linux because it was causing the ProS3 to enter REPL
  - run `sudo service modemmanager stop` in the linux terminal
  - Need to investigate handling the issue in the microcontroller's code
  - Need to uninstall the modemmanager
  - Need to create script in linux to check if modemmanager is running at startup and kill it

**01/26/2024**
- Worked on electronics side instead of code
  - want to get a relay output circuit put together so that I can toggle a solenoid using the code
- Got a first draft of the relay driver circuit drawn in KiCAD and approved by Andrew and Jordan
  - using optocoupler to drive a relay with an indicator LED and freewheel/flyback diode in parallel across the relay coil
  - want to use active low pins to drive the circuit according to Andrew

**01/29/2024**
- Talked with Andrew about pin modes for output
  - Want to go with push pull if using on board voltage regulator (current plan)
  - use open drain with internal pull up if using separate voltage regulator
- Verified oring sizing for manifold block using Erik online gland calculator
- Ordered oring and screws to connect top and bottom half of manifold block

**01/30/2024**
- Looked into adding a watchdog timer to reboot the ProS3 in the event of a communication failure or code error
  - Will need the watchdog timer running on the ProS3 and periodic data being sent by the plugin inside of pathpilot
  - Want to set up the pathpilot plugin to send data every ~2 seconds (pick some time interval that feels comfortable) and call feed() on the ProS3 every time data is received
- Also looked at non-blocking LED blink
  - Will want to make the responses to serial communication non blocking on the ProS3 and make the serial write commands in pathpilot nonblocking
 
**02/01/2024**
- Tried adding a watchdog timer triggered by first successful serial communication on a 2 second timer
  - 2 seconds is way too fast for development purposes, and watchdog should be triggered by a specific serial command/start phrase
  - Got stuck in a boot loop here's how to fix:
    - To get into safe mode, follow these steps:
      1. Press the [RESET] button to reset the ESP32-S3 chip
      2. After the RGB LED has gone purple and then off, press and hold the [BOOT] button for a few seconds
      Your board should now be in safe mode.
