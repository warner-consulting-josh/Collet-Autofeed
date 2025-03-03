# Collet-Autofeed

Automation of Collets on the Tormach Slant Pro lathe using a custom tooling block, individually addressable coolant lines controlled by an [UnexpectedMaker ProS3](https://esp32s3.com/pros3.html) and ui_hooks.py, and custom G-code for auto stock advance.

## Description

This project uses the uihooks.py [Plugin controller](http://xoomspeed.com/CNC/pathpilot/plugins/uihooks.htm) created by David Loomes at XoomSpeed, to run custom python code for interacting with a ProS3 microcontroller which in turn controls solenoids to direct the coolant stream to the currently active tool. We've also implemented custom G-code to auto advance the stock after each part with a GUI for inputting the stock length at the beginning of the run. (The stock input GUI only works on earlier versions of PathPilot, but it is not reequired for the rest of the system to function)
The hardware includes a custom tooling block, a manifold for the solenoids, a main board with the microcontroller and relays, a connector board to break out the relay lines, and enclosures for both boards.

## Getting Started

### Dependencies

* PathPilot V2
* PathPilot Plugins by [Xoomspeed](http://xoomspeed.com/CNC/pathpilot/plugins.htm)

### Installing

* Follow the instructions from [Xoomspeed](http://xoomspeed.com/CNC/pathpilot/plugins.htm) for intstalling the PathPilot Plugin framework
   * The specific plugin for running the coolant controller is [here:](https://github.com/warner-consulting-josh/Collet-Autofeed/blob/main/PathPilot%20Python/ProS3Cool_plugin.py)
* The circuitpython code that runs on the microcontroller is [here:](https://github.com/warner-consulting-josh/Collet-Autofeed/blob/main/ProS3%20CircuitPython/code.py)
   * Note that the file must be named code.py for the microcontroller using circuitpython to recognize and run it 

### Circuit Boards

* Gerber files for ordering the circuit boards are [here:](https://github.com/warner-consulting-josh/Collet-Autofeed/tree/main/KiCAD/Addressable_Coolant_Controller/gerber_to_order)
* boards were designed in KiCAD using a multi-board workflow with [KiKit](https://yaqwsx.github.io/KiKit/v1.4/multiboard/)

## Authors

Contributors names and contact info

Josh Warner  
joshua@warner-consulting.com

## Version History

* 1.0.0
    * Initial Release

## License

This project is licensed under the [GPL-3.0-only](https://opensource.org/license/gpl-3-0) License

## Acknowledgments

Inspiration, code snippets, etc.
* [XoomSpeed](http://xoomspeed.com/index.htm)
* [KiKit](https://yaqwsx.github.io/KiKit/v1.4/)
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
