# Notes
Need to find ways of ensuring that modemmanager does not kick the ProS3 into REPL
- Try this: [Addition to rules file](https://www.metrel.si/support/confluence/mpd/en/software-troubleshooting/how-to-communicate-with-instruments-under-linux#:~:text=On%20most%20Linux%20distributions%20ModemManager,to%20use%20specific%20USB%20device)
- and this: [rules file](https://www.downtowndougbrown.com/2016/10/fix-for-usb-serial-port-being-opened-by-modemmanager-at-startup/)
- [remove modemmanager](https://superuser.com/questions/568502/usb-device-blocked-at-startup-by-modem-manager) if the above doesn't work
- See if there is a way to ignore the commands in the circuitpython code
