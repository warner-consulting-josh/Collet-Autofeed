# Notes

**Code**
Need to find ways of ensuring that modemmanager does not kick the ProS3 into REPL
- Try this: [Addition to rules file](https://www.metrel.si/support/confluence/mpd/en/software-troubleshooting/how-to-communicate-with-instruments-under-linux#:~:text=On%20most%20Linux%20distributions%20ModemManager,to%20use%20specific%20USB%20device)
- and this: [rules file](https://www.downtowndougbrown.com/2016/10/fix-for-usb-serial-port-being-opened-by-modemmanager-at-startup/)
- [remove modemmanager](https://superuser.com/questions/568502/usb-device-blocked-at-startup-by-modem-manager) if the above doesn't work
- See if there is a way to ignore the commands in the circuitpython code

**Electronics**
Need to design PCBA
- Relay outputs
  - Look at this [suggestion](https://electronics.stackexchange.com/questions/449872/relay-control-by-using-microcontroller) using optocouplers
  - Relay Options:
    - [R57-1D.5-24D](https://www.digikey.com/en/products/detail/nte-electronics-inc/R57-1D-5-24D/11651064)
    - [G5V-1-T90 DC24](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/G5V-1-T90-DC24/6650357)
- Connection to solenoids
  - VDW22JA by SMC bought [here](https://us.misumi-ec.com/vona2/detail/221006494761/?HissuCode=VDW22JA&PNSearch=VDW22JA&searchFlow=results2type&KWSearch=VDW22JA&Tab=catalog&curSearch=%7b%22field%22%3a%22%40search%22%2c%22seriesCode%22%3a%22221006494761%22%2c%22innerCode%22%3a%22%22%2c%22sort%22%3a1%2c%22specSortFlag%22%3a0%2c%22allSpecFlag%22%3a0%2c%22page%22%3a1%2c%22pageSize%22%3a%2260%22%2c%2200000030955%22%3a%22b%22%2c%2200000030968%22%3a%22g%22%2c%2200000030971%22%3a%22b%22%2c%2200000030965%22%3a%22mdm00000000000003%22%2c%22SP910002396%22%3a%22mdm00000000000006%22%2c%22SP910002397%22%3a%22mdm00000000000001%22%2c%22SP910002399%22%3a%22mdm00000000000001%22%2c%22SP910002400%22%3a%22mdm00000000000001%22%2c%22SP910002401%22%3a%22mdm00000000000001%22%2c%22SP910002402%22%3a%22mdm00000000000001%22%2c%22fixedInfo%22%3a%22innerCode%3aMDM00012160730%7c19%22%7d)
  - Power consumption: 3W
  - Voltage: 24 Vdc
  - Current: 125 mA
- Socket for ProS3?
  - ESP32-S3 GPIO pins each can source 40mA max, prefer to keep at 20mA (does this need power other than USB?)
- Power input
  - 3.3v or 5v for ProS3?
  - 24v for solenoids?
