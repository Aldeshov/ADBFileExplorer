# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import sys
from typing import Union

from app.core.configurations import Settings
from app.core.managers import PythonADBManager, ADBManager, WorkersManager
from app.helpers.tools import Singleton
from app.services import adb


# Optional libs
try:
    import adb_shell
except ImportError:
    adb_shell = None


class Adb(metaclass=Singleton):
    PYTHON_ADB_SHELL = 'python'  # Python library `adb-shell`
    EXTERNAL_TOOL_ADB = 'external'  # Command-line tool `adb`

    core = Settings.adb_core()

    @classmethod
    def start(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            if adb.kill_server().IsSuccessful:
                print("adb server stopped.")

            if adb_shell is not None:
                print('Using Python "adb-shell" version %s' % adb_shell.__version__)
            else:
                print('Python "adb-shell" is not installed. Install it with "pip install adb-shell"')

        elif cls.core == cls.EXTERNAL_TOOL_ADB and adb.validate():
            print(adb.version().OutputData)

            adb_server = adb.start_server()
            if adb_server.ErrorData:
                print(adb_server.ErrorData, file=sys.stderr)

            print(adb_server.OutputData or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                name = PythonADBManager.get_device().name if PythonADBManager.get_device() else "Unknown"
                print('Connection to device %s closed' % name)
                PythonADBManager.device.close()
            return True

        elif cls.core == cls.EXTERNAL_TOOL_ADB:
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped")
            return True

    @classmethod
    def manager(cls) -> Union[ADBManager, PythonADBManager]:
        if cls.core == cls.PYTHON_ADB_SHELL:
            return PythonADBManager()
        elif cls.core == cls.EXTERNAL_TOOL_ADB:
            return ADBManager()

    @classmethod
    def worker(cls) -> WorkersManager:
        return WorkersManager()
