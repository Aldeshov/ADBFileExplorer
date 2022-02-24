import logging
from typing import List, Union

from PyQt5.QtCore import QObject
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

from data.models import File, Device
from helpers.tools import Communicate, Singleton, get_python_rsa_keys_signer, AsyncRepositoryWorker


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
        if not cls.device or not cls.device.available:
            try:
                cls.connect(device.id)
                return True
            except BaseException as error:
                logging.error(error)
                return False


class WorkersManager:
    """
    General (Base) Workers Manager
    Contains a list of workers
    """
    __metaclass__ = Singleton
    instance = QObject()
    workers: List[AsyncRepositoryWorker] = []

    @classmethod
    def work(cls, worker: AsyncRepositoryWorker) -> bool:
        for _worker in cls.workers:
            if _worker == worker or _worker.id == worker.id:
                if _worker.closed:
                    cls.workers.remove(_worker)
                    del _worker
                    break
                logging.error(
                    f"Cannot create Worker {worker.name}, {worker.id=}! "
                    f"There already have a Worker {_worker.name} with id {_worker.id}!"
                )
                return False
        worker.setParent(cls.instance)
        cls.workers.append(worker)
        return True


class PythonADBWorkerManager(WorkersManager):
    """
    Workers Manager for `python-adb` and `adb-shell` libraries:
    Reason: these libraries accept only one command per device.
    Therefor, one worker per application
    """
    @classmethod
    def work(cls, worker: AsyncRepositoryWorker) -> bool:
        if len(cls.workers) > 0:
            if not cls.workers[0].closed:
                logging.error(
                    f"Cannot create Worker {worker.name}, {worker.id=}! "
                    f"There already have a Worker! class[PythonADBWorkerManager]"
                )
                return False
            cls.workers.pop(0)
        worker.setParent(cls.instance)
        cls.workers.append(worker)
        return True


class Global:
    __metaclass__ = Singleton
    communicate = Communicate()
