# coding=utf-8
#-----------------------------------------------------------------------
# Copyright Â© 2022 XoomSpeed All rights reserved.
# License: GPL Version 2
# Written by David Loomes 7/10/22
# 24/01/23  Added StateDescriptor and StateMachine classes
# 27/03/23  Added debug output for state controller
# 27/03 Added StateTime() method to state controller to track time in current state
#-----------------------------------------------------------------------

# if this file exists in ~/gcode/python/ui_hooks.py the UI will import it
# once running, this module searches for other plugins named *_plugin.py
# Any plugins found are loaded and a single instance of the class UserPlugin()
# implemented by the pklugin is created.
# This module also provides class plugin() which is intended as a base clasee
# for the imported plugins.  This base class provides access to LinuxCNC command
# and status objects together with error_handler that facilitates sending
# messages to the PathPilot status screen 

# PathPilot constants
import constants

# Some standard python modules
from threading import Thread
import time
import glob
import os
import subprocess
import sys

# the linuxcnc python interfaces
import linuxcnc

# some global variables the plugins will be able to use
# their values come from the PathPilot UI when the plug in system is initialised
global halCommand
global error_handler
global version_list
global dig_output_offset

# one instance of this class created by PathPilot UI during startup
class ui_hooks():

    def __init__(self, linuxcnc_command, err_handler, ver_list, digital_output_offset=0):
        # copy our incoming parameters to global variables so the plugins can get access
        global halCommand
        halCommand = linuxcnc_command
        
        global error_handler
        error_handler = err_handler
        
        global version_list
        version_list = ver_list
        
        # digital_output_offset is for the lathe config where USBIO outputs start at '5' and mill config they start at output '0'
        global dig_output_offset
        dig_output_offset = digital_output_offset

        # can test PathPilot version if needed
        # ver_list = [major int, minor int, build int, suffix_string ]
        error_handler.write('PathPilot version: %s.%s.%s' % (version_list[0], version_list[1], version_list[2]), constants.ALARM_LEVEL_QUIET)

        # log that we were found
        error_handler.write('ui_hooks:__init__() called', constants.ALARM_LEVEL_DEBUG)

        # create an empty list of loaded plugins
        self.plugins = []

        # and load any we can find
        self.LoadPlugins()

        # then process any hal files
        self.RunHalFiles()

    def RunHalFiles(self):
        # get a list of all hal files
        halNames = glob.glob('/home/operator/gcode/python/*_plugin.hal')
        for halName in halNames:
            p = subprocess.Popen(["halcmd", "-i", sys.argv[2], "-f", halName])
            p.wait()
            if p.returncode != 0:
                msg = 'Error: halcmd returned {:d} from {}'.format(p.returncode, halName)
                error_handler.write(msg, constants.ALARM_LEVEL_QUIET)


    # called during startup to load and initialise the plugins    
    def LoadPlugins(self):
        # get a list of all plugins
        plugInNames = glob.glob('/home/operator/gcode/python/*_plugin.py')

        # load each plugin in turn
        for pathName in plugInNames:
            try:
                # extract the module name from the path
                fileName = os.path.basename(pathName).rpartition(".py")[0]

                # import the user module
                usermod = __import__(fileName)

                # create the plugin object instance and add it to our list
                plugInObject = usermod.UserPlugin()

                # check it has the correct base class
                if isinstance(plugInObject, plugin):
                    # add it to our list if it has the correct base
                    self.plugins.append(plugInObject)
                else:
                    error_handler.write('%s is not an instance of plugin' % (plugInObject,))


            except BaseException as err:
                error_handler.write('Error occurred starting plugin: %s - %s' % (pathName, err))

    # the following methods are called by the PathPilot UI in response to particular UI events
    # the plugin manager simply calls the equivalent method in each loaded plug in

    def stop_button(self):
        # tell all the loaded plugins that the stop button ha been pressed
        for plugin in self.plugins:
            plugin.stop_button_pressed()

    def reset_button(self):
        # tell all the loaded plugins that the reset button ha been pressed
        for plugin in self.plugins:
            plugin.reset_button_pressed()

    def estop_event(self):
        # tell all the loaded plugins that the e-stop button ha been pressed
        for plugin in self.plugins:
            plugin.estop_event()

class StateDescriptor:
    def __init__(self, _stateName, _onEnter, _onUpdate, _onLeave):
        # remember the constructor's parameters
        self.stateName = _stateName
        self.onEnter = _onEnter
        self.onUpdate = _onUpdate
        self.onLeave = _onLeave

    def Enter(self, machine):
        if self.onEnter != None :
            self.onEnter(machine)

    def Update(self, machine):
        if self.onUpdate :
            self.onUpdate(machine)

    def Leave(self, machine):
        if self.onLeave != None:
            self.onLeave(machine)

class StateMachine:
    def __init__(self, showDebugMessage = None):
        self.stateDict = {}
        self.state = 0
        self.ShowDebugMsg = showDebugMessage

        # set the entry time for the starting state
        self.stateStartTime = time.time()


    def AddState(self, stateID, stateDesc):
        # store the new state in the dictionary
        self.stateDict[stateID] = stateDesc

        # if it's the first one, make it current
        if len(self.stateDict) == 1:
            self.state = stateID

    def Update(self):
        # just call the current state's update method
        self.stateDict[self.state].Update(self)

    def ChangeState(self, newState):
        # nothing to do unless the state is actually changing
        if newState != self.state :
            if self.ShowDebugMsg != None:
                self.ShowDebugMsg("Leaving state " + self.stateDict[self.state].stateName)

            # leave the old state
            self.stateDict[self.state].Leave(self)

            # change the current state
            self.state = newState

            # and remember the entry time
            self.stateStartTime = time.time()

            if self.ShowDebugMsg != None:
                self.ShowDebugMsg("Entering state " + self.stateDict[self.state].stateName)

            # enter the new state
            self.stateDict[self.state].Enter(self)

    def StateTime(self):
        return time.time() - self.stateStartTime


# this is the base class for plugins
# its most useful function is to provide simple member access to the global variables at the top of this module
class plugin():
    def __init__(self, plugin_name):
        # create my own halstatus object
        self.halStatus = linuxcnc.stat()

        # remember my name
        self.name = plugin_name

        # fetch copies of other global objects
        self.halCommand = halCommand
        self.error_handler = error_handler
        self.ver_list = version_list
        # digital_output_offset is for the lathe config where USBIO outputs start at '5' and mill config they start at output '0'
        self.digital_output_offset = dig_output_offset

        # tell the world I've been loaded
        self.error_handler.write('Loaded plugin - %s' % (self.name,), constants.ALARM_LEVEL_QUIET)

    # a convenient way for the derived class to display message on the status screen
    def ShowMsg(self, msg, errLevel=constants.ALARM_LEVEL_QUIET):
        self.error_handler.write("{} Plugin : {}".format(self.name, msg), errLevel)


    # the plugin class may override any of the following methods to pick up UI events

    def stop_button_pressed(self):
        return

    def reset_button_pressed(self):
        return

    def estop_event(self):
        return