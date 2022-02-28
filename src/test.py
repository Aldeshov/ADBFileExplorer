# ADB File Explorer `tool`
# Copyright (C) 2022  Azat Aldeshov azata1919@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from adb_shell.adb_device import AdbDeviceUsb

from helpers.tools import get_python_rsa_keys_signer

device = AdbDeviceUsb()
device.connect(rsa_keys=[get_python_rsa_keys_signer()], auth_timeout_s=0.1)


if __name__ == "__main__":
    files = device.list('/sdcard/Download/')
    for file in files:
        print(file)
