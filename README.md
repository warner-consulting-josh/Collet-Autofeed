# Collet-Autofeed

Automation of Collets on the Tormach Slant Pro lathe using a custom tooling block, individually addressable coolant lines controlled by an [UnexpectedMaker ProS3](https://esp32s3.com/pros3.html) and ui_hooks.py, and custom G-code for auto stock advance.

## Description

This project uses the uihooks.py [Plugin controller](http://xoomspeed.com/CNC/pathpilot/plugins/uihooks.htm) created by David Loomes at XoomSpeed, to run custom python code for interacting with a ProS3 microcontroller which in turn controls solenoids to direct the coolant stream to the currently active tool. We've also implemented custom G-code to auto advance the stock after each part with a GUI for inputting the stock length at the beginning of the run.
The hardware includes a custom tooling block, a manifold for the solenoids, a driver board for the solenoids and a watertight enclosure to house the electronics.

## Getting Started

### Dependencies

* PathPilot V2
* ex. Windows 10

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

Josh Warner  
joshua@warner-consulting.com

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
