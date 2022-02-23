from typing import Union

import adb_shell

from core.managers import PythonADBManager, AndroidADBManager
from helpers.tools import Singleton
from services import adb


class Adb:
    __metaclass__ = Singleton

    PYTHON_ADB = 0
    COMMON_ANDROID_ADB = 1

    instances = (
        (PYTHON_ADB, "Python library `python-adb`"),
        (COMMON_ANDROID_ADB, "Android external tool `adb`")
    )

    __instance__ = instances[COMMON_ANDROID_ADB]  # Experimental

    @classmethod
    def instance(cls):
        return cls.__instance__[0]

    @classmethod
    def instance_description(cls):
        return cls.__instance__[1]

    @classmethod
    def start(cls):
        if cls.instance() == cls.PYTHON_ADB:
            # Exiting from adb
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped.")

            print(f'Using `python-adb` and `adb_shell` libraries')
            print(f'Python adb-shell version {adb_shell.__version__}')
            return True

        elif cls.instance() == cls.COMMON_ANDROID_ADB:
            # Validate ADB and start server
            adb.validate()
            print(adb.version().OutputData)

            # Start adb server
            adb_server = adb.start_server()
            print(adb_server.OutputData or adb_server.ErrorData or 'ADB server running...')
            return True

    @classmethod
    def stop(cls):
        if cls.instance() == cls.PYTHON_ADB:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                print(f'Connection to device {PythonADBManager.get_device().name} closed')
                PythonADBManager.device.close()
            return True

        elif cls.instance() == cls.COMMON_ANDROID_ADB:
            if adb.kill_server().IsSuccessful:
                print("ADB Server stopped")
            return True

    @classmethod
    def manager(cls) -> Union[AndroidADBManager, PythonADBManager]:
        if cls.instance() == cls.PYTHON_ADB:
            return PythonADBManager()
        elif cls.instance() == cls.COMMON_ANDROID_ADB:
            return AndroidADBManager()
