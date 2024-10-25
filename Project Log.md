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
    - `sudo apt-get purge modemmanager`

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

**02/05/2024**
- Adjusted watchdog timer to 45s and implemented a keyword to start watchdog ('ProS3')
  - Not sure that keyword is working as intended
  - watchdog timer stays active through resets, may need to actively disable it in code until the keyword is received
  - need to work through the logic of what should happen in the event of failure:
    - Pause the g-code running on the tormach?
    - keep the current coolant solenoid energized? or turn them all off?
    - restart g-code if connection to microcontroller reestablished?
    - wait for user input?
    - only pause if connection not reestablished with X seconds?
    - Talk with EW and make a plan
- Added `print(microcontroller.cpu.reset_reason)` to display the reason for the last time the code was stopped
  - would like to have this displayed on a screen, along with current tool, up time since last reset?

**02/07/2024**
- Removed watchdog timer and added code to toggle gpio pin based on serial input
  - Successfully implemented active low gpio triggering
- Breadboarded relay circuit but had trouble getting relay to trigger

**02/08/2024**
- Found issue with breadboard circuit
  - Flyback diode was reversed which prevented the relay from triggering
- Having some issues with the timing of the LED blink, so will need to look at difference between old and new code

**02/12/2024**
- Added KiCAD to github repository for version control and sync across computers
- Added 24v monitor circuit to circuit schematic
  - Plan to send an error/pause command up to the plugin if 24v power is lost
- Added 4 pin connector for power in of same style as ribbon cable connector that goes to the solenoid connection daughter board
  - Plan to have input daughter board with power in and USB in
- Looked at screens
  - Currently have small monochrome OLED [screen](https://www.adafruit.com/product/938)
  - Maybe want bigger [screen?](https://www.adafruit.com/product/5872)
    - Look into power requirements, and how difficult it is to drive each screen
   
**02/15/2024**
- Got KiCAD integrated fully into github using a submodule for the custom libraries
  - Created a separate repository for the [custom libraries](https://github.com/warner-consulting-josh/Warner-Consulting-Libraries.git)
  - Used git bash to add submodule to Collet-Autofeed repository which acts like a symbolic link pointing back to the libraries repository
    - `git submodule add https://github.com/warner-consulting-josh/Warner-Consulting-Libraries.git KiCAD/Warner-Consulting-Libraries`
  - Need to use `git submodule update --remote --merge` any time there are changes to the libraries repository (adding componnets, updating step files, etc.)
- Evaluated several header connectors and replaced the Wurth one with a TE AMP-Latch [connector](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/1761685-6/2187846)

**03/01/2024**
- Successfully integrated basic display code with serial read code
  - Displayed current tool number on OLED using Mu, Pathpilot virtual machine, and actual lathe
- Need to decide what information to display
  - Current tool
  - Reason for last restart
  - Up time?
    - Will this cause issues with code blocking?
- Need to get larger screen
  - E-ink?
  - Big OLED?
  - Colored screen?

**09/03/2024**
- Powered up breadboard circuit and confirmed code works and displays current tool
  - Confirmed code working with Mu, and Pathpilot virtual machine
- Tried to get wrapper .nc program running for multiple part operation
  - Ran into issue with remapped M-Codes
  - Need to investigate further because I had this working before
  - Look into remap.py and the INI file for the lathe
  - Have python with remaps defined, need to figure out how exactly it was integrated into pathpilot

**09/05/2024**
- Worked on getting custom M-code working again
- Did not find anything terribly useful
  - Most links seem to just point back at the one post that shows how to make the M codes but doesn't have a solution to the index out error
- This was working at some point in the past
  - Maybe boot up old laptop and see if you can make it function there

**09/06/2024**
- Continued working on getting custom M-codes working
- Booted old laptop and have functioning code in onld version of pathpilot
- Same code does not work in new version of pathpilot
- Code is having trouble calling dialog = Tk()
  - When I run this on it's own in python, it works
  - It looks like pathpilot is using python 2.7, not 3.x
- Added an error message to M20 and it forced an error immediately on loading Gcode, not when I run it

**09/09/2024**
- Continued with custom M-codes
- Caused and then fixed error: parameter file name missing
  - Don't comment out any of the remaps in the remap file
- Currently dealing with is_calable(oword.m22remap) = FALSE
- Stripped the remapped M-code functions down to only displaying messages that they were called, but no message shows up, likely due to the above
- Probably also part of why the dialog boxes are not functioning
- Further research on the linuxcnc forum required

**09/10/2024**
- Figured out how to snapshot virtualbox
- Updated pathpilot inside virtualbox to latest version 2.10.1
- This erased my changes in the .ini and custom M-code stuff, so I will need to re-introduce them to test if this still has the issue with nested python calls

**09/24/2024**
- As far as I can tell, I will not be able to get user prompting running under later versions of PathPilot
  - Will need to revert machine to v2.2.4 (figure out latest version that will work)
- Got subroutine code working
  - Needed endif statement for every if statement (elseif does not function as endif)
  - Needed endsub for one of the routines
- Got external named subroutine working
  - Needed to add subroutine path to .ini file
  - Need to make sure subroutine file is executable
  - o<filename> sub/endsub/call (where filename is the name of the subroutine file without the .nc extension)
- Moved groove and advance code into external subroutine
- Need to move body and nut code into external subroutines
- Need to add grooving stock requirement to part per bar calculations
- Need to add part number override for running n parts explicitly until we get user prompting working

**09/30/2024**
- Got the code transfered over to the lathe and have collets running multiples at a time
  - Need to copy the working code from the lathe into the github so that it is accurately represented
- Looked at the state of electronics
  - Enclosure and connectors that I had previously ordered
  - Drew a crude architecture diagram, need to transfer that into a more refined format draw.io?
  - Plan to have small enclosure on lathe bed with connections to relays on a board that connects to a larger (10 pin) cable
  - 10 pin cable connects to main board in housing that is stationary
    - Either mounted on wall or on operator console
  - Main board enclosure has screeen, relays, microcontroller, power connection, relay control connection, USB connection
    - USB will be pass through (have gland pieces)
    - Power and relay control will be snap lock type connectors
    - No ribbon cable, no daughterboard in this enclosure
    - Will need to mount screen in here somehow
      - Don't want to block relay LEDs
      - Can use little connector cable directly from micro, or could use pins and headers
     
**10/03/2024**
- Drew a basic architecture diagram in draw.io
- Started designing relay connector board and enclosure
  - Will use 10 pin connector and snap lock to connect to PCB with 8x 2 pin connectors
  - Plan to machine enclosure from solid piece of delrin and use O-ring to seal lid
    - 3D print before machining to ensure everything fits
   
**10/08/2024**
- Finished design of relay connector board enclosure
- Need to double check O-ring gland design
- Will be machined from large block of delrin with clear acrylic lid
- Need to adjust mounting board to fit new design
- Need to work on PCB layout for connector board
- Need to work on design of enclosure for main board with screen

**10/11/2024**
- Tried using big screen, looked like more effort than I was up for this morning
- Do we actually need big screen?
  - Screen is more of a diagnostic tool/passive information display
  - Focus should be on getting system functional and then adding features later if we want them
  - Design enclosure for small screen and deal with big screen later
- System is fucntioning, so we should get some PCBs and enclosure
- Need to machine solenoid manifold
- Need to machine connector board enclosure

**10/14/2024**
- Added `ignore = dirty` to gitmodule file to deal with untracked changes issue in github
- Started placing components into mcmaster washdown enclosure, but had to deal with github issues for most of the morning

**10/15/2024**
- Replaced ribbon cable connector with 10-pin molex connector on main board schematic
- Started placing connectors and board supports in mcmaster enclosure model
- Fixed issues with libraries and added library for molex connector
- Need to double check that libraries are properly syncing because one of my footprints was missing
- Need to add board clearance to board support piece

**10/17/2024**
- Actually fixed issue with submodule
  - Had created file inside mirrored folder instead of in base repository folder, see notes for details
- Added 2 pin power connector to schematic
- Updated board outline to new size and started positioning components

**10/22/2024**
- Placed components on PCB and completed initial routing
- Still need to add power and ground planes
- Need to figure out why labels are not showing on silk screen
- Need to add silk screen demarkations for solenoid to LED correlations
- Probably should add a logo and some other identifying information to the silk screen as well

**10/23/2024**
- Replaced PC365NJ0000F surface mount opto-isolator with PC12311NSZ1B through hole
- Added power and ground fills on top and bottom layers respectively
- Need to figure out why changes to 10-pin and 2-pin connectors didn't save/propagate to other computer
- Need to figure out silkscreen labels not showing for components

**10/24/2024**
- Added rectangle representing screen into the silkscreen layer
- Sketched screen board outline in solidworks in the part file of the box
- Need to figure out screw size and standoffs
- Need to add screw holes into main board
  - Consider 3d printed screen support as alternative
  - Might be somewhat spidery, but maybe it would work with standoffs
 
**10/25/2024**
- Fixed silkscreen labels for components
  - Had to mess with library footprints and update the footprints on the pcb
- Replaced remaining surface mount opto-isolator with through hole
- Adjusted screen mount to used OTS standoffs
