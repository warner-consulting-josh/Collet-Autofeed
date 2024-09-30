# Notes

**Code**

Need to find ways of ensuring that modemmanager does not kick the ProS3 into REPL
- Try this: [Addition to rules file](https://www.metrel.si/support/confluence/mpd/en/software-troubleshooting/how-to-communicate-with-instruments-under-linux#:~:text=On%20most%20Linux%20distributions%20ModemManager,to%20use%20specific%20USB%20device)
- and this: [rules file](https://www.downtowndougbrown.com/2016/10/fix-for-usb-serial-port-being-opened-by-modemmanager-at-startup/)
- [remove modemmanager](https://superuser.com/questions/568502/usb-device-blocked-at-startup-by-modem-manager) if the above doesn't work
- See if there is a way to ignore the commands in the circuitpython code

Need to figure out how I got custom M-codes fucntioning in the past to prompt the user for bar length and part type
- Look into remap.py and figure out what you did with it before
- Have a file named custom_m_code.py
  - Figure out how to plug this into pathpilot
  - Do I copy paste into the existing tormach remap file?
  - Do I add something to toplevel.py?
- Try following instructions [here](https://forum.linuxcnc.org/20-g-code/33642-custom-m-code-python)
- Confirmed to have working version of remapped M-codes on old pathpilot virtual machine
  - Looking into differences between two versions
  - Found some minor differences, but correcting the file in the new pathpilot did not address the issue
    - This is likely a pathpilot version difference that is causing the problem, something with Tkinter.py
  - The issue is occuring when calling M22, it seems like M20 is parsed immediately when the Gcode is loaded
    - Is my list being lost?
    - Add lots of comments/error messages to figure out where things are going wrong
- **parameter file name is missing**
  - This is caused when you comment out one of the remap definitions
  - Will cause linuxcnc to hang and become non-responsive
  - If you have anything called out as remapped in the ini file make sure it is defined in the remap.py file
- is_callable(oword.m22remap) = FALSE
  - Need to figure out how to fix this to get messages to print, probably also part of the issue in getting the dialog boxes working
  - This error is related to python files calling other python files
    - You can only go 2 layers deep before it stops functioning
    - Effecctively that means all python needs to be in remap.py because it can't call other python files properly
    - linuxcnc forum user bevins discovered this bug and it doesn't appear to have been fixed as of yet
    - likely this makes it impossible to use the custom M-code architecture for user prompting under newer versions of pathpilot
    - will check with latest release 2.10.1

**Electronics**

Need to design PCBA - Use [KiCAD](https://www.kicad.org/)
- Relay outputs
  - Look at this [suggestion](https://electronics.stackexchange.com/questions/449872/relay-control-by-using-microcontroller) using optocouplers
    - Andrew suggested that I don't need the external BJT since the chosen optocoupler has an internal one sufficient to drive the relay directly
    - Andrew suggested to use active low signal with push pull mode if using the on board voltage regulator
      - if using a separate voltage regulator, use open drain mode with internal pull up resistor enabled
      - [here](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html) is how to set the pin mode
    - added an indicator LED across the relay coil directly so that we know when the relay is supposed to be on visually
  - Relay Options:
    - [G5V-1-T90 DC24](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/G5V-1-T90-DC24/6650357)
  - LED:
    - [150120BS75000](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/150120BS75000/4489933)
  - Optocoupler:
    - [PC365NJ0000F](https://www.digikey.com/en/products/detail/sharp-socle-technology/PC365NJ0000F/720501)
- Connection to solenoids
  - VDW22JA by SMC bought [here](https://us.misumi-ec.com/vona2/detail/221006494761/?HissuCode=VDW22JA&PNSearch=VDW22JA&searchFlow=results2type&KWSearch=VDW22JA&Tab=catalog&curSearch=%7b%22field%22%3a%22%40search%22%2c%22seriesCode%22%3a%22221006494761%22%2c%22innerCode%22%3a%22%22%2c%22sort%22%3a1%2c%22specSortFlag%22%3a0%2c%22allSpecFlag%22%3a0%2c%22page%22%3a1%2c%22pageSize%22%3a%2260%22%2c%2200000030955%22%3a%22b%22%2c%2200000030968%22%3a%22g%22%2c%2200000030971%22%3a%22b%22%2c%2200000030965%22%3a%22mdm00000000000003%22%2c%22SP910002396%22%3a%22mdm00000000000006%22%2c%22SP910002397%22%3a%22mdm00000000000001%22%2c%22SP910002399%22%3a%22mdm00000000000001%22%2c%22SP910002400%22%3a%22mdm00000000000001%22%2c%22SP910002401%22%3a%22mdm00000000000001%22%2c%22SP910002402%22%3a%22mdm00000000000001%22%2c%22fixedInfo%22%3a%22innerCode%3aMDM00012160730%7c19%22%7d)
  - Power consumption: 3W
  - Voltage: 24 Vdc
  - Current: 125 mA
- Socket for ProS3?
  - ESP32-S3 GPIO pins each can source 40mA max, prefer to keep at 20mA (does this need power other than USB?)
- Power input
  - 3.3v or 5v for ProS3?
    - can accept both, will be getting some power from the usb (500mA?)
    - might want isolated voltage regulator for powering optcouplers? (total current draw = ?)
  - 24v for solenoids and relays

High Level Architecture
- Main board with micro controller socket, relays, LEDs, screen connection
  - Housed in waterproof enclosure with clear top, either on wall or next to operator screen
- Daughter board with relay connector sockets, big cable connector socket
  - Housed in waterproof enclosure mounted to lathe bed
  - Single cable running back to main board
- Connector board with socket for power, big cable, and USB (maybe passthrough)
  - Housed in same enclosure as Main board
  - Connects to main board with ribbon cable
- Board for screen?
