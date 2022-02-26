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
    __DEVICE__: Union[Device, None] = None

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
            return f"{host}:{port}"

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
    workers: List[AsyncRepositoryWorker] = []

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
