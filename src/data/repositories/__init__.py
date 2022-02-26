from typing import List

from core.daemons import Adb
from data.models import Device, File
from data.repositories import android_adb, python_adb


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.file(path=path)
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.file(path=path)

    @classmethod
    def files(cls) -> (List[File], str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.files()
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.files()

    @classmethod
    def download(cls, progress_callback: callable, source: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.download(progress_callback=progress_callback, source=source)
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.download(progress_callback=progress_callback, source=source)

    @classmethod
    def download_to(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.download_to(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.download_to(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.new_folder(name=name)
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.new_folder(name=name)

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.DeviceRepository.devices()
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.DeviceRepository.devices()

    @classmethod
    def connect(cls, device_id) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.DeviceRepository.connect(device_id=device_id)
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.DeviceRepository.connect(device_id=device_id)

    @classmethod
    def disconnect(cls) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB:
            return python_adb.DeviceRepository.disconnect()
        elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
            return android_adb.DeviceRepository.disconnect()
