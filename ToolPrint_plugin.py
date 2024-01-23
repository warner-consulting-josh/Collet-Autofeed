# coding=utf-8
#-----------------------------------------------------------------------
# Copyright Â© 2022 XoomSpeed All rights reserved.
# License: GPL Version 2
# Written by David Loomes 7/10/22
#-----------------------------------------------------------------------

# this module implements a plugin that ensures the spindle cannot be turned on while the spindle is loaded


# import some python modules
from threading import Thread
import time

# definitions of linuxcnc python interfaces
import linuxcnc

# PathPilot constants
import constants

# base class for plugins
from ui_hooks import plugin

# the tuple of tool numbers to prtect from spinlde on
PROBE_TOOL_NUMBERS = (99,)

# time(s) between spindle checks when the probe is loaded
SHORT_SLEEP_TIME = 0.1

# time(s) between spindle checks when the probe is not loaded
LONG_SLEEP_TIME = 1.0

# the plugin class
# one instance is created by ui_hooks.py during system load
# a python Thread (monitorProbe) is used to check the tool number and spindle status
# if the spindle is turned on while tool 99 is loaded, abort() is called

class UserPlugin(plugin):
    # Last tool variable
    lastTool = 0
    def __init__(self):
        # initialise the base class, specifying a name for this plugin
        plugin.__init__(self, 'Tool Print')

        # start the worker thread
        self.toolPrintthread = Thread(target=self.toolPrint)
        self.toolPrintthread.daemon = True
        self.toolPrintthread.start()

        # define a variable for the last tool that was active
        


    def toolPrint(self):
        self.ShowMsg('Tool Print thread is running')

        while True:
            # make sure hal status info is up to date
            self.halStatus.poll()

            # what is the current tool?
            if self.halStatus.tool_in_spindle != self.lastTool:
                # current tool is a new tool
                self.lastTool = self.halStatus.tool_in_spindle
                self.error_handler.write('Current Tool: %s' % (self.halStatus.tool_in_spindle))

                # with a new tool, short sleep before checking again
                time.sleep(SHORT_SLEEP_TIME)
            else:
                # tool hasn't changed, so sleep for longer before checkng again
                time.sleep(LONG_SLEEP_TIME)
