# ADB File Explorer

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

Simple cross-platform File Explorer for adb devices. Uses Python library [`adb-shell`](https://github.com/JeffLIrion/adb_shell) or command-line tool [`adb`](https://developer.android.com/studio/command-line/adb).

Note

- This project is currently not actively maintained. Bug reports, recommendations, and improvements are welcome via issues and pull requests.

Features:

* List of adb devices
* Connect via IP (TCP)
* Listing / Pulling / Pushing files
* Renaming and Deleting files


## 1. Screenshots

Devices & Notifications

<img src="https://user-images.githubusercontent.com/47108137/159409583-a2106cb3-e39c-4d29-9226-e44daadaec72.png" width="480" alt="Devices & Notifications">

Files

<img src="https://user-images.githubusercontent.com/47108137/159409633-98662fda-b919-4b3a-ac39-230534a5a839.png" width="480" alt="Files">


## 2. Requirements

* `Python 3.8+` (older versions are not tested)
* `PyQt5`
* `adb` ([Android Platform Tools](https://developer.android.com/tools/releases/platform-tools)) if you choose the external `adb` implementation (default)
* Optional: `adb-shell` and `libusb1` (only needed if you choose the Python implementation of ADB inside the app)


External `adb` vs Python `adb-shell`

- You can choose which ADB core to use in [settings.json](src%2Fapp%2Fsettings.json):
  - `external` — use the system `adb` binary (default, recommended for simplicity). In this case you do NOT need `libusb1` or `adb-shell`.
  - `python` — use `adb-shell` (pure Python). If you want to communicate over USB, you will need `libusb1` plus OS-specific libs/drivers (below). For TCP/IP connections, `libusb1` is not required.


## 3. Install

### 3.1 Prerequisites

Installing and preparing Python (if not already installed)

- Ubuntu/Debian (Linux)
  ```shell
  sudo apt-get update
  sudo apt-get install -y python3 python3-pip python3-venv
  python3 -m pip install --upgrade pip setuptools wheel
  ```
- macOS (Homebrew)
  ```shell
  brew update
  brew install python@3
  python3 -m pip install --upgrade pip setuptools wheel
  ```
- Windows (PowerShell)
  ```powershell
  winget install Python.Python.3
  py -m pip install --upgrade pip setuptools wheel
  ```

OS-specific prerequisites only for `adb-shell` + `libusb1` (skipped if you choose the external `adb` implementation)

- Linux: install `libusb-1.0-0` (runtime) and set proper udev rules so that your user can access the device without root. For example:
  ```shell
  sudo apt-get install -y libusb-1.0-0
  # Optional but recommended: Android udev rules
  # See https://github.com/M0Rf30/android-udev-rules or your distro's package
  ```
- macOS: install libusb via Homebrew:
  ```shell
  brew install libusb
  ```
- Windows: install a WinUSB driver for your device using Zadig:
  - Download Zadig: https://zadig.akeo.ie/
  - Connect your Android device, open Zadig, select the device, choose WinUSB, and click Install Driver.
  - This is only required for the `adb-shell + libusb1` path, not for the external `adb` binary.
  - Also for dependencies of `adb-shell` you may need Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

### 3.2 Dependencies and environment

1. Download or `git clone https://github.com/Aldeshov/ADBFileExplorer.git`
2. `cd ADBFileExplorer`
3. Create virtual environment by running `python3 -m venv venv` (Linux/macOS) or `py -m venv venv` (Windows)
4. Activate virtual environment by running `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
5. Install requirements:
   - Option A: Full installation (external adb + optional python adb):
     ```shell
     pip install -r requirements.txt
     ```
   - Option B: Manual installation:
     ```shell
     pip install PyQt5 # (external adb only)
     pip install adb-shell libusb1 # (If you plan to use the Python adb implementation)
     ```
   - In newer python versions, you may need to install `setuptools` manually:
     ```shell
     pip install setuptools
     ```

## 4. App settings (`src/app/settings.json`)

```json5
{
  "adb_path": "adb", // Full adb path, or just "adb" if the executable is in `$PATH`
  "adb_core": "external", // Set to "external" to use system `adb` executable, or "python" to use `adb-shell`
  "adb_kill_server_at_exit": false, // Stop adb server on app exit
  "preserve_timestamp": true, // Preserve file timestamps when pushing files
  "adb_run_as_root": false // Run adb as root
}
```

Note: The example above uses JSON5-style comments for explanation. The actual file `src/app/settings.json` is standard JSON and does not support comments.


## 5. Run the app

- Using helper scripts:
  - Linux/macOS: `./run.sh`
  - Windows: `run.bat`
- Or directly with Python from the project root:
  ```shell
  # Linux/macOS
  python3 -m src.app
  # Windows
  py -m src.app
  ```


## 6. License

```text
ADB File Explorer [python-app]
Copyright (C) 2025  Azat Aldeshov

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
