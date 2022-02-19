import typing
from typing import List

from config import Default
from services.data.drivers import convert_to_devices, convert_to_file, convert_to_file_list_a, convert_to_lines
from services.data.managers import FileManager
from services.data.models import File, Device, FileType
from services.shell import adb


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if not FileManager.get_device() or not path:
            return None, "Invalid arguments"

        path = FileManager.clear_path(path)
        args = adb.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ')]
        response = adb.shell(FileManager.get_device(), args)
        if not response.Successful:
            return None, response.ErrorData or response.OutputData

        file = convert_to_file(response.OutputData.strip())
        if not file:
            return None, response.ErrorData or f"Unexpected string:\n{response.OutputData}"

        if file.type == FileType.LINK:
            args = adb.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ') + '/']
            response = adb.shell(FileManager.get_device(), args)
            file.link_type = FileType.UNKNOWN
            if response.OutputData and response.OutputData.startswith('d'):
                file.link_type = FileType.DIRECTORY
            elif response.OutputData and response.OutputData.__contains__('Not a'):
                file.link_type = FileType.FILE
        file.path = path
        return file, response.ErrorData

    @classmethod
    def files(cls) -> (List[File], str):
        if not FileManager.get_device() or not FileManager.path():
            return [], "Invalid arguments"
        path = FileManager.path()
        args = adb.ShellCommand.LS_ALL_LIST + [path.replace(' ', r'\ ')]
        response = adb.shell(FileManager.get_device(), args)
        if not response.Successful and response.ExitCode != 1:
            return [], response.ErrorData or response.OutputData

        if not response.OutputData:
            return [], response.ErrorData

        args = adb.ShellCommand.LS_ALL_DIRS + [path.replace(' ', r'\ ') + "*/"]
        response_dirs = adb.shell(FileManager.get_device(), args)
        if not response_dirs.Successful and response_dirs.ExitCode != 1:
            return [], response_dirs.ErrorData or response_dirs.OutputData

        dirs = convert_to_lines(response_dirs.OutputData)
        files = convert_to_file_list_a(response.OutputData, dirs=dirs, path=path)
        return files, response.ErrorData

    @classmethod
    def download(cls, source: str, async_fun: typing.Callable):
        if FileManager.get_device() and source:
            adb.pull(FileManager.get_device(), source, Default.device_downloads_path(), async_fun)

    @classmethod
    def download_to(cls, source: str, destination: str, async_fun: typing.Callable):
        if FileManager.get_device() and source and destination:
            adb.pull(FileManager.get_device(), source, destination, async_fun)

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if not FileManager.get_device() or not name:
            return None, "Invalid arguments"

        args = [adb.ShellCommand.MKDIR, f'{FileManager.path()}{name}'.replace(' ', r"\ ")]
        response = adb.shell(FileManager.get_device(), args)
        if not response.Successful:
            return None, response.ErrorData or response.OutputData

        return response.OutputData, response.ErrorData

    @classmethod
    def upload(cls, source: str, async_fun: typing.Callable):
        if FileManager.get_device() and FileManager.path() and source:
            adb.push(FileManager.get_device(), source, FileManager.path(), async_fun)


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        response = adb.devices()
        if not response.Successful:
            return [], response.ErrorData or response.OutputData

        devices = convert_to_devices(response.OutputData)
        # for index, device in enumerate(devices):
        #     response = adb.shell(device.id, adb.ShellCommand.GETPROP_PRODUCT_MODEL)
        #     if response.Successful and response.OutputData is not None:
        #         devices[index].name = response.OutputData.strip()
        return devices, response.ErrorData

    @classmethod
    def connect(cls, device_id) -> (str, str):
        if not device_id:
            return None, "Invalid arguments"

        response = adb.connect(device_id)
        if not response.Successful:
            return None, response.ErrorData or response.OutputData

        return response.OutputData, response.ErrorData

    @classmethod
    def disconnect(cls) -> (str, str):
        response = adb.disconnect()
        if not response.Successful:
            return None, response.ErrorData or response.OutputData

        return response.OutputData, response.ErrorData
