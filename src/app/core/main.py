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

from app.core.managers import PythonADBManager, ADBManager, WorkersManager
from app.helpers.tools import Singleton
from app.services import adb


class Adb:
    __metaclass__ = Singleton

    PYTHON_ADB_SHELL = 0  # Python library `adb-shell`
    EXTERNAL_TOOL_ADB = 1  # Command-line tool `adb`

    CORE = PYTHON_ADB_SHELL

    @classmethod
    def start(cls):
        if cls.CORE == cls.PYTHON_ADB_SHELL:
            if adb.kill_server().IsSuccessful:
                print("adb server stopped.")

            print('Using Python "adb-shell" version %s' % adb_shell.__version__)

        elif cls.CORE == cls.EXTERNAL_TOOL_ADB and adb.validate():
            print(adb.version().OutputData)

            adb_server = adb.start_server()
            if adb_server.ErrorData:
                print(adb_server.ErrorData, file=sys.stderr)

            print(adb_server.OutputData or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.CORE == cls.PYTHON_ADB_SHELL:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                name = PythonADBManager.get_device().name if PythonADBManager.get_device() else "Unknown"
                print('Connection to device %s closed' % name)
                PythonADBManager.device.close()
            return True

        elif cls.CORE == cls.EXTERNAL_TOOL_ADB:
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped")
            return True

    @classmethod
    def manager(cls) -> Union[ADBManager, PythonADBManager]:
        if cls.CORE == cls.PYTHON_ADB_SHELL:
            return PythonADBManager()
        elif cls.CORE == cls.EXTERNAL_TOOL_ADB:
            return ADBManager()

    @classmethod
    def worker(cls) -> WorkersManager:
        return WorkersManager()

    @classmethod
    def set_core(cls, core: int):
        if core == cls.PYTHON_ADB_SHELL:
            cls.CORE = cls.PYTHON_ADB_SHELL
        elif core == cls.EXTERNAL_TOOL_ADB:
            cls.CORE = cls.EXTERNAL_TOOL_ADB

    @classmethod
    def current_core(cls):
        if cls.CORE == cls.PYTHON_ADB_SHELL:
            return 'PYTHON_ADB_SHELL'
        elif cls.CORE == cls.EXTERNAL_TOOL_ADB:
            return 'EXTERNAL_TOOL_ADB'
