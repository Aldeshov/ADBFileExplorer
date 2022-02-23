import logging
from typing import List, Union

from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from data.models import File, Device
from helpers.tools import Communicate, Singleton, get_python_rsa_keys_signer


class AndroidADBManager:
    __metaclass__ = Singleton

    __PATH__: List[str] = []
    __DEVICE__: Union[Device, None]

    @classmethod
    def path(cls) -> str:
        result = '/'
        for path in cls.__PATH__:
            result += f'{path}/'
        return result

    @classmethod
    def open(cls, file: File) -> bool:
        if not cls.__DEVICE__:
            return False

        if file.isdir and file.name:
            cls.__PATH__.append(file.name)
            return True
        return False

    @classmethod
    def go(cls, file: File) -> bool:
        if file.isdir and file.location:
            cls.__PATH__.clear()
            for name in file.path.split('/'):
                cls.__PATH__.append(name) if name else ''
            return True
        return False

    @classmethod
    def up(cls) -> bool:
        if cls.__PATH__:
            cls.__PATH__.pop()
            return True
        return False

    @classmethod
    def get_device(cls) -> Device:
        return cls.__DEVICE__

    @classmethod
    def set_device(cls, device: Device) -> bool:
        if device:
            cls.clear_device()
            cls.__DEVICE__ = device
            return True

    @classmethod
    def clear_device(cls):
        cls.__DEVICE__ = None
        cls.__PATH__.clear()

    @staticmethod
    def clear_path(path: str) -> str:
        result = ''
        array = path.split('/')
        for name in array:
            result += f'/{name}' if name else ''
        if not result:
            return '/'
        return result


class PythonADBManager(AndroidADBManager):
    device: Union[AdbDeviceUsb, AdbDeviceTcp] = None
    signer: PythonRSASigner = get_python_rsa_keys_signer()

    @staticmethod
    def connect(device_id, port: int = 5555, tcp: bool = False):  # IMPORTANT! throws exceptions -> use try | except
        if tcp:
            PythonADBManager.device = AdbDeviceTcp(device_id, port, default_transport_timeout_s=9.)
        else:
            PythonADBManager.device = AdbDeviceUsb()
        PythonADBManager.device.connect(rsa_keys=[PythonADBManager.signer], auth_timeout_s=1.)

    @classmethod
    def set_device(cls, device: Device) -> bool:
        super(PythonADBManager, cls).set_device(device)
        try:
            cls.connect(device.id)
            return True
        except BaseException as error:
            logging.error(error)
            return False


class Global:
    __metaclass__ = Singleton
    communicate = Communicate()
