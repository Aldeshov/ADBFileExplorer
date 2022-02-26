# ADB File Explorer `tool` `python`

Simple File explorer for adb devices. Uses python `adb-shell` library or external `adb` (android-tool).
Features:

* List of adb devices
* Connect via IP (TCP)
* List of files / folders / other types of files
* Pulling files / folders
* Pushing files / folders

## Screenshots

Devices

<img src="https://user-images.githubusercontent.com/47108137/155853630-ccb32071-9cf0-4702-9db9-694f6bba1f22.png" width="480">

Files & Notifications

<img src="https://user-images.githubusercontent.com/47108137/155853637-2a6f912e-7f3c-46d5-abeb-732591c1b938.png" width="480">

## Requirements

* `Python >= 3.8` (other versions not tested)
* Virtual environment (optional)
* pip installation with `requirements.txt`
* `adb` (android-tool) should exist in project root folder or in `PATH` variables

## Project

`res` folder - project resources

`src` folder - project source code

`src` / `app.py` file - start point of the application

## Intro

File `src` / `core` / `daemons.py`

```python
class Adb:
...
    CORE = PYTHON_ADB
    # PYTHON_ADB to use library `adb-shell`
    # COMMON_ANDROID_ADB to use Android external tool `adb`
...
```

`python src/app.py` - to start application

## `adb` vs `adb-shell`

[+] `adb` faster than python library and can perform multiple operations at the same time 

[-] `adb` harder to convert output data from command line (progress callback does not work properly)

[+] `adb-shell` no need of adb tool or daemon, progress callback for pulling / pushing exists and works properly

[-] `adb-shell` only one command per device at a time, more dependencies, slower due to `python`, etc...

## License

```
ADB File Explorer `tool` `python`
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

## Additional

```python
# TODO("New features")
# [TAB] File -> Settings
# [TAB] Tools -> APK Manager
# [ACTION] File Properties -> Copy file
# [ACTION] File Properties -> Move file
# [ACTION] File Properties -> Rename file
# [ACTION] File Properties -> Delete file
```

