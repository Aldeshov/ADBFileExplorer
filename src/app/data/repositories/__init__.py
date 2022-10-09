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

from typing import List

from app.core.main import Adb
from app.data.models import Device, File
from app.data.repositories import android_adb, python_adb


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.file(path=path)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.file(path=path)

    @classmethod
    def files(cls) -> (List[File], str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.files()
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.files()

    @classmethod
    def rename(cls, file: File, name: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.rename(file, name)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.rename(file, name)

    @classmethod
    def open_file(cls, file: File) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.open_file(file)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.open_file(file)

    @classmethod
    def delete(cls, file: File) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.delete(file)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.delete(file)

    @classmethod
    def download(cls, progress_callback: callable, source: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.download(progress_callback=progress_callback, source=source)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.download(progress_callback=progress_callback, source=source)

    @classmethod
    def download_to(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.download_to(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.download_to(
                progress_callback=progress_callback,
                source=source,
                destination=destination
            )

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.new_folder(name=name)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.new_folder(name=name)

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.devices()
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.devices()

    @classmethod
    def connect(cls, device_id) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.connect(device_id=device_id)
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.connect(device_id=device_id)

    @classmethod
    def disconnect(cls) -> (str, str):
        if Adb.CORE == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.disconnect()
        elif Adb.CORE == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.disconnect()
