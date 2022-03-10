# ADB File Explorer `tool` `python`

Simple File Explorer for adb devices. Uses python library [`adb-shell`](https://github.com/JeffLIrion/adb_shell) or command-line tool [`adb`](https://developer.android.com/studio/command-line/adb?hl=ru).

Features:

* List of adb devices
* Connect via IP (TCP)
* Listing / Pulling / Pushing files
* Renaming and Deleting files

## Screenshots

Devices

<img src="https://user-images.githubusercontent.com/47108137/155853630-ccb32071-9cf0-4702-9db9-694f6bba1f22.png" width="480" alt="Devices">

Files & Notifications

<img src="https://user-images.githubusercontent.com/47108137/155853637-2a6f912e-7f3c-46d5-abeb-732591c1b938.png" width="480" alt="Files & Notifications">

## Requirements

* `Python3` (below version 3.8 not tested)
```shell
pip install PyQt5 libusb1 adb-shell
```
* `adb` (binary) should exist in project root folder or in `PATH` variables

## Launch

File `src` / `app.py`

```python
from core.main import Adb
# ...
if __name__ == '__main__':
    adb = Adb()
    adb.set_core(Adb.EXTERNAL_TOOL_ADB)  # To use command-line tool `adb`
    adb.start()
# ...
```

```shell
python src/app.py # To start application
```

## Attention

Application by default uses `adb-shell`.
There may be problems with listing, pushing, pulling files using `adb-shell`.
Use the adb command line tool for a better experience

## License

```
ADB File Explorer `python-tool`
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