import logging
from typing import Union

import adb_shell

from core.managers import PythonADBManager, AndroidADBManager, WorkersManager
from helpers.tools import Singleton
from services import adb


class Adb:
    __metaclass__ = Singleton

    PYTHON_ADB = 0  # Python library `adb-shell`
    COMMON_ANDROID_ADB = 1  # Android external tool `adb`

    CORE = PYTHON_ADB

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
                logging.error(adb_server.ErrorData)

            print(adb_server.OutputData or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.CORE == cls.PYTHON_ADB:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                print(f'Connection to device {PythonADBManager.get_device().name} closed')
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
