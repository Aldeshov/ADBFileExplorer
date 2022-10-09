# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import logging
import posixpath

from PyQt5.QtCore import QObject
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb

from app.data.models import File, Device
from app.helpers.tools import Communicate, Singleton, get_python_rsa_keys_signer, AsyncRepositoryWorker


class ADBManager:
    __metaclass__ = Singleton

    __path = []
    __device = None

    @classmethod
    def path(cls) -> str:
        return posixpath.join('/', *cls.__path) + '/' if cls.__path else '/'

    @classmethod
    def open(cls, file: File) -> bool:
        if not cls.__device:
            return False

        if file.isdir and file.name:
            cls.__path.append(file.name)
            return True
        return False

    @classmethod
    def go(cls, file: File) -> bool:
        if file.isdir and file.location:
            cls.__path.clear()
            for name in file.path.split('/'):
                cls.__path.append(name) if name else ''
            return True
        return False

    @classmethod
    def up(cls) -> bool:
        if cls.__path:
            cls.__path.pop()
            return True
        return False

    @classmethod
    def get_device(cls) -> Device:
        return cls.__device

    @classmethod
    def set_device(cls, device: Device) -> bool:
        if device:
            cls.clear()
            cls.__device = device
            return True

    @classmethod
    def clear(cls):
        cls.__device = None
        cls.__path.clear()

    @staticmethod
    def clear_path(path: str) -> str:
        return posixpath.normpath(path)


class PythonADBManager(ADBManager):
    signer = get_python_rsa_keys_signer()
    device = None

    @classmethod
    def connect(cls, device_id: str) -> str:
        if device_id.__contains__('.'):
            port = 5555
            host = device_id
            if device_id.__contains__(':'):
                host = device_id.split(':')[0]
                port = device_id.split(':')[1]
            cls.device = AdbDeviceTcp(host=host, port=port, default_transport_timeout_s=10.)
            cls.device.connect(rsa_keys=[cls.signer], auth_timeout_s=1.)
            return '%s:%s' % (host, port)

        cls.device = AdbDeviceUsb(serial=device_id, default_transport_timeout_s=3.)
        cls.device.connect(rsa_keys=[cls.signer], auth_timeout_s=30.)
        return device_id

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
    Async Workers Manager
    Contains a list of workers
    """
    __metaclass__ = Singleton
    instance = QObject()
    workers = []

    @classmethod
    def work(cls, worker: AsyncRepositoryWorker) -> bool:
        for _worker in cls.workers:
            if _worker == worker or _worker.id == worker.id:
                cls.workers.remove(_worker)
                del _worker
                break
        worker.setParent(cls.instance)
        cls.workers.append(worker)
        return True

    @classmethod
    def check(cls, worker_id: int) -> bool:
        for worker in cls.workers:
            if worker.id == worker_id:
                if worker.closed:
                    return True
                return False
        return False


class Global:
    __metaclass__ = Singleton
    communicate = Communicate()
