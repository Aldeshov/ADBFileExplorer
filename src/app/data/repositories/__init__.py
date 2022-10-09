# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from typing import List

from app.core.main import Adb
from app.data.models import Device, File
from app.data.repositories import android_adb, python_adb


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.file(path=path)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.file(path=path)

    @classmethod
    def files(cls) -> (List[File], str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.files()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.files()

    @classmethod
    def rename(cls, file: File, name: str) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.rename(file, name)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.rename(file, name)

    @classmethod
    def open_file(cls, file: File) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.open_file(file)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.open_file(file)

    @classmethod
    def delete(cls, file: File) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.delete(file)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.delete(file)

    @classmethod
    def download(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.new_folder(name=name)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.new_folder(name=name)

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.devices()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.devices()

    @classmethod
    def connect(cls, device_id) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.connect(device_id=device_id)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.connect(device_id=device_id)

    @classmethod
    def disconnect(cls) -> (str, str):
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.disconnect()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.disconnect()
