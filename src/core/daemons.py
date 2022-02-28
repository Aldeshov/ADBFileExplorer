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

import sys
from typing import Union

import adb_shell

from core.managers import PythonADBManager, AndroidADBManager, WorkersManager
from helpers.tools import Singleton
from services import adb


class Adb:
    __metaclass__ = Singleton

    PYTHON_ADB = 0  # Python library `adb-shell`
    COMMON_ANDROID_ADB = 1  # Android external tool `adb`

    CORE = PYTHON_ADB  # PYTHON_ADB / COMMON_ANDROID_ADB

    def __init__(self):
        if self.CORE == self.PYTHON_ADB:
            # Exiting from adb
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped.")

            print(f'Using Python `adb-shell` version {adb_shell.__version__}')

        elif self.CORE == self.COMMON_ANDROID_ADB and adb.validate():
            print(adb.version().OutputData)

            # Start adb server
            adb_server = adb.start_server()
            if adb_server.ErrorData:
                print(adb_server.ErrorData, file=sys.stderr)

            print(adb_server.OutputData or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.CORE == cls.PYTHON_ADB:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                name = PythonADBManager.get_device().name if PythonADBManager.get_device() else "Unknown"
                print(f'Connection to device {name} closed')
                PythonADBManager.device.close()
            return True

        elif cls.CORE == cls.COMMON_ANDROID_ADB:
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped")
            return True

    @classmethod
    def manager(cls) -> Union[AndroidADBManager, PythonADBManager]:
        if cls.CORE == cls.PYTHON_ADB:
            return PythonADBManager()
        elif cls.CORE == cls.COMMON_ANDROID_ADB:
            return AndroidADBManager()

    @classmethod
    def worker(cls) -> WorkersManager:
        return WorkersManager()
