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
