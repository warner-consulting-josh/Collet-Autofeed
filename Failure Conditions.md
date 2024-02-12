# Failure Conditions and Response Strategies
**Failure Modes**
1. Power loss to microcontroller
2. Power loss to solenoids
3. Code crash
4. Serial communication lost

**General Thoughts**
- Not haveing coolant isn't like not having air, more like not having water
  - Need to fix the problem, but don't need to stop instantaneously
  - Have ~30-60s to respond?
- Want to check status of microcontroller after each operation?
  - Don't like that this needs to be added to the G-code
    - might be able to detect an operation change similar to how a tool change is detected
    - don't like the variability in length of time of the operations (time without coolant could be as long as longest operation)
  - Would prefer to have the status check built into the plugin
- Want to check the status of microcontroller every X seconds?
  - "Hearbeat" sent from microcontroller and listened to by plugin
  - Watchdog timer on microcontroller to reset in case of code failure
- How many times/how long should plugin try to reconnect before issuing a pause command?
  - use "TryToConnect" function for X seconds or X times
- Should we have a fallback coolant nozzle that is fixed to the headstock?
  - turns on if there are issues with the plugin/microcontroller
  - allows finishing current part?
- Want to display message about why the microcontroller failed/reset/restarted
  - send message to plugin
  - also display on small screen directly on microcontroller
  - have a running timer showing how long the microcontroller has been functioning since last reset

**Response Strategies**
1. Power loss to microcontroller
   - leads to serial communication lost
   - try to reestablish communication within acceptable time frame using plugin code
   - else, pause program 
3. Power loss to solenoids
   - leads to no coolant flowing from nozzles
   - could have fallback nozzle that is "fail safe" ie. is the default path that is diverted away from when a solenoid is powered
   - want to feed info about solenoid power back into microcontroller
   - if power not restored to solenoids within X seconds, send pause message to plugin
5. Code crash
   - leads to serial communication lost
   - use watchdog timer to reset microcontroller
   - try to reestablish communication within acceptable time frame using plugin code
   - else, pause program 
7. Serial communication lost
   - try to reestablish communication within acceptable time frame using plugin code
   - else, pause program 
