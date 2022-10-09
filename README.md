# ADB File Explorer

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

Simple File Explorer for adb devices. Uses python library [`adb-shell`](https://github.com/JeffLIrion/adb_shell) or command-line tool [`adb`](https://developer.android.com/studio/command-line/adb).

Features:

* List of adb devices
* Connect via IP (TCP)
* Listing / Pulling / Pushing files
* Renaming and Deleting files

## Screenshots

Devices & Notifications

<img src="https://user-images.githubusercontent.com/47108137/159409583-a2106cb3-e39c-4d29-9226-e44daadaec72.png" width="480" alt="Devices & Notifications">

Files

<img src="https://user-images.githubusercontent.com/47108137/159409633-98662fda-b919-4b3a-ac39-230534a5a839.png" width="480" alt="Files">

## Requirements

* `Python3` (below version 3.8 not tested)
```shell
sudo apt-get install python3-pyqt5  # For Linux Ubuntu
pip install PyQt5 libusb1 adb-shell
```
* `adb` (binary) should exist in project root folder or in `PATH` variables

## Launch

File `settings.json`. Settings file.
Currently, this file may be created anywhere in project folders, Usually in `src` or root folder.

```json
{
  "adb_path": "adb",
  "adb_core": "external",
  "adb_kill_server_at_exit": false,
  "preserve_timestamp": true,
  "adb_run_as_root": false
}
```

+ `adb_path` - Full adb path or just 'adb' if executable is in the PATH variables
+ `adb_core` - Set 'external' to use external adb executable, otherwise app will use `adb-shell`

... etc

```shell
cd ADBFileExplorer
# First install python-venv in root folder
pip install -r requirements.txt
run.bat # To start application on Windows
bash run.sh # To start application on Linux...
```

## Attention

Application by default uses `adb-shell`.
There may be problems with listing, pushing, pulling files using `adb-shell`.
Use the adb command line tool for a better experience

## License

```text
ADB File Explorer [python-app]
Copyright (C) 2022  Azat Aldeshov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
