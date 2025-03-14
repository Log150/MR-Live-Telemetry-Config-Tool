# MR-Live-Telemetry-Config-Tool

## Overview

This is the Mizzou Racing Live Telemetry Configuration Tool. This application lets you create JSON files with the proper formating for Mizzou Racing's Live Telemetry system.
The app was made for Mizzou Racing by members of Mizzou Racing. While the funcationality of the tool is directed at our Live Telemetry system, we hope that everyone who wants to will be able to use this tool to configure whatever they need. While we want this tool to be used, we the developers humbly ask that all direct uses retain the "Mizzou Live Telemetry Config Tool" tag at the top of the page, and that all forks give due credit in their ReadMe and somewhere visible on the application. Enjoy!

## Features

- Create new JSON files properly formatted for the Live Telemetry system
- Load multiple JSON files at once
- Add new configurations
- Edit existing configurations
- Create paddock config from loaded files

## Usage Guide
### Installation
Download and run the latest version from https://github.com/Log150/MR-Live-Telemetry-Config-Tool/releases/tag/release

If you would like to compile from source:
It is first recommended to have an updated version of git, python3, and PyQt5
1. Open the github page: https://github.com/Log150/MR-Live-Telemetry-Config-Tool
2. Read this ReadMe to ensure you understand the applications and limitations of this tool
3. Run the following command in the directory of your choice to clone the repository 
(this will clone it as a new folder, so be careful not to unnecessarily nest repos)
```
git clone https://github.com/Log150/MR-Live-Telemetry-Config-Tool
```
4. Once the repo has finished cloning, attempt to run the executable. If this does not work, attempt to run the python code with the below command:
```
cd dev
python3 'Live Telemetry Config Maker.py'
```
5. If the python works but the executable does not, see the instructions for creating a new executable below

### Developer's Guide

This code is implmented using mainly python3, and PyQt5. There are abundant resources
online for learning how to use these. The executable file was created using pyinstaller. If changes
are made to the "/dev/Live Telemetry Config Maker.py", an undated .exe can be made with the following command run
from the root directory:
```
pyinstaller --onefile --add-data './dev/styles.qss:.' -w './dev/Live Telemetry Config Maker.py'
```

### Simplest Usage Case
1. Open the app
2. Create or load a JSON formatted for the Live Telemetry system (like what can be found in dev/ExampleData/)
3. Add a new configuration or edit an existing one
4. Save the file
5. Create Paddock from file

### Contributing

All are welcome to contribute to this project. If you would like to make updates please make a branch
to work on and create a pull request if you want your code merged into main. Alternatively, if you want
to make and maintain your own changes, all are welcome to fork this repo, but as stated previously, we
humbly request that you maintain some visible credit to our original project, in addition to the 
license as specified below.

### License and Copyright

This project is licensed under the MIT License - see the LICENSE file for details.
