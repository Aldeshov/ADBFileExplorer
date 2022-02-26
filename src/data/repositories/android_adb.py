from typing import List

from core.configurations import Default
from core.managers import AndroidADBManager
from data.models import FileType, Device, File
from helpers.converters import convert_to_devices, convert_to_file, convert_to_file_list_a
from services import adb


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if not AndroidADBManager.get_device():
            return None, "No device selected!"

        path = AndroidADBManager.clear_path(path)
        args = adb.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ')]
        response = adb.shell(AndroidADBManager.get_device().id, args)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData

        file = convert_to_file(response.OutputData.strip())
        if not file:
            return None, f"Unexpected string:\n{response.OutputData}"

        if file.type == FileType.LINK:
            args = adb.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ') + '/']
            response = adb.shell(AndroidADBManager.get_device().id, args)
            file.link_type = FileType.UNKNOWN
            if response.OutputData and response.OutputData.startswith('d'):
                file.link_type = FileType.DIRECTORY
            elif response.OutputData and response.OutputData.__contains__('Not a'):
                file.link_type = FileType.FILE
        file.path = path
        return file, response.ErrorData

    @classmethod
    def files(cls) -> (List[File], str):
        if not AndroidADBManager.get_device():
            return None, "No device selected!"

        path = AndroidADBManager.path()
        args = adb.ShellCommand.LS_ALL_LIST + [path.replace(' ', r'\ ')]
        response = adb.shell(AndroidADBManager.get_device().id, args)
        if not response.IsSuccessful and response.ExitCode != 1:
            return [], response.ErrorData or response.OutputData

        if not response.OutputData:
            return [], response.ErrorData

        args = adb.ShellCommand.LS_ALL_DIRS + [path.replace(' ', r'\ ') + "*/"]
        response_dirs = adb.shell(AndroidADBManager.get_device().id, args)
        if not response_dirs.IsSuccessful and response_dirs.ExitCode != 1:
            return [], response_dirs.ErrorData or response_dirs.OutputData

        dirs = response_dirs.OutputData.split()
        files = convert_to_file_list_a(response.OutputData, dirs=dirs, path=path)
        return files, response.ErrorData

    @classmethod
    def download(cls, progress_callback: callable, source: str) -> (str, str):
        destination = Default.device_downloads_path(AndroidADBManager.get_device())
        return cls.download_to(progress_callback, source, destination)

    class UpDownHelper:
        def __init__(self, callback: callable):
            self.messages = []
            self.callback = callback

        def call(self, data: str):
            if data.startswith('['):
                progress = data[1:4].strip()
                if progress.isdigit():
                    self.callback(data[7:], int(progress))
            elif data:
                self.messages.append(data)

    @classmethod
    def download_to(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if AndroidADBManager.get_device() and source and destination:
            helper = cls.UpDownHelper(progress_callback)
            response = adb.pull(AndroidADBManager.get_device().id, source, destination, helper.call)
            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if not AndroidADBManager.get_device():
            return None, "No device selected!"

        args = [adb.ShellCommand.MKDIR, f'{AndroidADBManager.path()}{name}'.replace(' ', r"\ ")]
        response = adb.shell(AndroidADBManager.get_device().id, args)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        if AndroidADBManager.get_device() and AndroidADBManager.path() and source:
            helper = cls.UpDownHelper(progress_callback)
            response = adb.push(AndroidADBManager.get_device().id, source, AndroidADBManager.path(), helper.call)
            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        response = adb.devices()
        if not response.IsSuccessful:
            return [], response.ErrorData or response.OutputData

        devices = convert_to_devices(response.OutputData)
        return devices, response.ErrorData

    @classmethod
    def connect(cls, device_id) -> (str, str):
        if not device_id:
            return None, None

        response = adb.connect(device_id)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def disconnect(cls) -> (str, str):
        response = adb.disconnect()
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData

        return response.OutputData, response.ErrorData
