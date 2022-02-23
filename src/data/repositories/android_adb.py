import os
import threading
from typing import List

from gevent import thread

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

    @classmethod
    def download_to(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if AndroidADBManager.get_device() and source and destination:
            observer = cls.DownloadObservation(progress_callback, source, destination)
            response = adb.pull(AndroidADBManager.get_device().id, source, destination)
            observer.finish()
            if not response.IsSuccessful:
                return None, response.ErrorData

            destination = os.path.join(destination, os.path.basename(os.path.normpath(source)))
            return f"Download successful!\nDest: {destination}", None
        return None, None

    # Experimental observing class
    class DownloadObservation:
        def __init__(self, progress_callback, source, destination):
            self.finished = False
            observer = threading.Thread(target=self.observe_download, args=(progress_callback, source, destination))
            observer.start()

        # Bad finishing
        def finish(self):
            self.finished = True

        def observe_download(self, progress_callback, source, destination):
            destination = os.path.join(destination, os.path.basename(os.path.normpath(source)))
            args = adb.ShellCommand.LS_LIST_DIRS + [source.replace(' ', r'\ ')]
            response = adb.shell(AndroidADBManager.get_device().id, args)
            size = response.OutputData.split()[3]
            if response.IsSuccessful and size.isdigit():
                written = 0
                while not self.finished:
                    thread.sleep(0.2)
                    if os.path.isfile(destination) or os.path.isdir(destination):
                        progress_callback(destination, int(os.path.getsize(destination) - written), int(size))
                        written = os.path.getsize(destination)
                return True
            progress_callback(destination, 1, 2)

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
            response = adb.push(AndroidADBManager.get_device().id, source, AndroidADBManager.path())
            if not response.IsSuccessful:
                return None, response.ErrorData

            return f"Upload successful!\nDest: {AndroidADBManager.path()}", None
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
