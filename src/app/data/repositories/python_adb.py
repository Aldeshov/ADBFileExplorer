# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import datetime
import logging
import os
import shlex
from typing import List

from app.core.configurations import Settings
from app.core.managers import PythonADBManager
from app.data.models import Device, File, FileType
from app.helpers.converters import __converter_to_permissions_default__
from app.services.adb import ShellCommand
from app.helpers.tools import build_test_d_batch_script, parse_test_d_batch_output

try:
    from usb1 import USBContext
except ImportError:
    USBContext = None

class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            path = PythonADBManager.clear_path(path)
            mode, size, mtime = PythonADBManager.device.stat(path)
            file = File(
                name=os.path.basename(os.path.normpath(path)),
                size=size,
                date_time=datetime.datetime.utcfromtimestamp(mtime),
                permissions=__converter_to_permissions_default__(list(oct(mode)[2:]))
            )

            if file.type == FileType.LINK:
                # Use a portable single-path batch script to detect if link points to a directory
                script = build_test_d_batch_script([path])
                response = PythonADBManager.device.shell(shlex.join(['sh', '-c', script]))
                status = parse_test_d_batch_output(response or '')
                file.link_type = FileType.UNKNOWN
                if path in status:
                    file.link_type = FileType.DIRECTORY if status[path] else FileType.FILE
            file.path = path
            return file, None

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    @classmethod
    def files(cls) -> (List[File], str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"

        files = []
        try:
            path = PythonADBManager.path()
            response = PythonADBManager.device.list(path)

            symlink_paths: List[str] = []

            for file in response:
                if file.filename.decode() == '.' or file.filename.decode() == '..':
                    continue

                permissions = __converter_to_permissions_default__(list(oct(file.mode)[2:]))
                link_type = None
                if permissions[0] == 'l':
                    # Defer to a batched single shell call below
                    symlink_paths.append(path + file.filename.decode())

                files.append(
                    File(
                        name=file.filename.decode(),
                        size=file.size,
                        path=(path + file.filename.decode()),
                        link_type=link_type,
                        date_time=datetime.datetime.utcfromtimestamp(file.mtime),
                        permissions=permissions,
                    )
                )

            # Batch resolve all symlink targets with one shell call
            if symlink_paths:
                try:
                    script = build_test_d_batch_script(symlink_paths)
                    output = PythonADBManager.device.shell(shlex.join(['sh', '-c', script]))
                    status = parse_test_d_batch_output(output or '')
                    for f in files:
                        if f.permissions and f.permissions[0] == 'l':
                            if f.path in status:
                                f.link_type = FileType.DIRECTORY if status[f.path] else FileType.FILE
                except BaseException:
                    # On any failure, we keep link_type as is (None) or previously set
                    pass

            return files, None

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return files, error

    @classmethod
    def rename(cls, file: File, name: str) -> (str, str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        if name.__contains__('/') or name.__contains__('\\'):
            return None, "Invalid name"

        try:
            args = [ShellCommand.MV, file.path, file.location + name]
            response = PythonADBManager.device.shell(shlex.join(args))
            if response:
                return None, response
            return None, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    @classmethod
    def open_file(cls, file: File) -> (str, str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            args = [ShellCommand.CAT, file.path]
            if file.isdir:
                return None, "Can't open. %s is a directory" % file.path
            response = PythonADBManager.device.shell(shlex.join(args))
            return response, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    @classmethod
    def delete(cls, file: File) -> (str, str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            args = [ShellCommand.RM, file.path]
            if file.isdir:
                args = ShellCommand.RM_DIR_FORCE + [file.path]
            response = PythonADBManager.device.shell(shlex.join(args))
            if response:
                return None, response
            return "%s '%s' has been deleted" % ('Folder' if file.isdir else 'File', file.path), None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    class UpDownHelper:
        def __init__(self, callback: callable):
            self.callback = callback
            self.written = 0
            self.total = 0

        def call(self, path: str, written: int, total: int):
            if self.total != total:
                self.total = total
                self.written = 0

            self.written += written
            self.callback(path, int(self.written / self.total * 100))

    @classmethod
    def download(cls, progress_callback: callable, source: str, destination: str = None) -> (str, str):
        if not destination:
            destination = Settings.device_downloads_path(PythonADBManager.get_device())

        helper = cls.UpDownHelper(progress_callback)
        destination = os.path.join(destination, os.path.basename(os.path.normpath(source)))
        if PythonADBManager.device and PythonADBManager.device.available and source:
            try:
                PythonADBManager.device.pull(
                    device_path=source,
                    local_path=destination,
                    progress_callback=helper.call
                )
                return "Download successful!\nDest: %s" % destination, None
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
                return None, error
        return None, None

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"

        try:
            args = [ShellCommand.MKDIR, (PythonADBManager.path() + name)]
            response = PythonADBManager.device.shell(shlex.join(args))
            return None, response

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        helper = cls.UpDownHelper(progress_callback)
        destination = PythonADBManager.path() + os.path.basename(os.path.normpath(source))
        if PythonADBManager.device and PythonADBManager.device.available and PythonADBManager.path() and source:
            try:
                PythonADBManager.device.push(
                    local_path=source,
                    device_path=destination,
                    progress_callback=helper.call
                )
                return "Upload successful!\nDest: %s" % destination, None
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
                return None, error
        return None, None


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        if USBContext is None:
            return [], 'USB library not found, install it with "pip install libusb1"'

        if PythonADBManager.device:
            PythonADBManager.device.close()

        errors = []
        devices = []
        for device in USBContext().getDeviceList(skip_on_error=True):
            for setting in device.iterSettings():
                if (setting.getClass(), setting.getSubClass(), setting.getProtocol()) == (0xFF, 0x42, 0x01):
                    try:
                        device_id = device.getSerialNumber()
                        PythonADBManager.connect(device_id)
                        device_name = " ".join(
                            PythonADBManager.device.shell(" ".join(ShellCommand.GETPROP_PRODUCT_MODEL)).split()
                        )
                        device_type = "device" if PythonADBManager.device.available else "unknown"
                        devices.append(Device(id=device_id, name=device_name, type=device_type))
                        PythonADBManager.device.close()
                    except BaseException as error:
                        logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
                        errors.append(str(error))

        return devices, str("\n".join(errors))

    @classmethod
    def connect(cls, device_id: str) -> (str, str):
        try:
            if PythonADBManager.device:
                PythonADBManager.device.close()
            serial = PythonADBManager.connect(device_id)
            if PythonADBManager.device.available:
                device_name = " ".join(
                    PythonADBManager.device.shell(" ".join(ShellCommand.GETPROP_PRODUCT_MODEL)).split()
                )
                PythonADBManager.set_device(Device(id=serial, name=device_name, type="device"))
                return "Connection established", None
            return None, "Device not available"

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error

    @classmethod
    def disconnect(cls) -> (str, str):
        try:
            if PythonADBManager.device:
                PythonADBManager.device.close()
                return "Disconnected", None
            return None, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
            return None, error
