# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import threading
from typing import List

from app.core.configurations import Settings
from app.core.managers import ADBManager
from app.data.models import FileType, Device, File
from app.helpers.converters import convert_to_devices, convert_to_file, convert_to_file_list_a
from app.helpers.tools import build_test_d_batch_script, parse_test_d_batch_output
from app.services import adb
import shlex


class FileRepository:
    @classmethod
    def file(cls, path: str) -> (File, str):
        if not ADBManager.get_device():
            return None, "No device selected!"

        path = ADBManager.clear_path(path)
        args = adb.ShellCommand.LS_LIST_DIRS + [path]
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)])
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData

        file = convert_to_file(response.OutputData.strip())
        if not file:
            return None, "Unexpected string:\n%s" % response.OutputData

        if file.type == FileType.LINK:
            # Prefer exit-code-based check: test -d will dereference symlink
            test_args = ['sh', '-c', f"test -d {shlex.quote(path)}"]
            test_resp = adb.shell(ADBManager.get_device().id, [shlex.join(test_args)])
            file.link_type = FileType.DIRECTORY if test_resp.IsSuccessful else FileType.FILE
        file.path = path
        return file, response.ErrorData

    # Таймаут на листинг каталога (секунды).
    # 25с — достаточно для большинства папок даже по Wi-Fi.
    FILES_TIMEOUT = 25

    @classmethod
    def files(cls) -> (List[File], str):
        if not ADBManager.get_device():
            return None, "No device selected!"

        path = ADBManager.path()
        args = adb.ShellCommand.LS_ALL_LIST + [path]
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)],
                             timeout=cls.FILES_TIMEOUT)
        if not response.IsSuccessful and response.ExitCode != 1:
            err = response.ErrorData or response.OutputData or ''
            # Понятное сообщение при таймауте/offline уже формируется в CommonProcess,
            # просто пробрасываем его
            return [], err

        if not response.OutputData:
            return [], response.ErrorData

        # Build files list first, then resolve symlink directory types individually
        files = convert_to_file_list_a(response.OutputData, dirs=[], path=path)

        # Resolve link types without relying on globbing — batch all checks in a single shell call
        symlink_paths = []
        for f in files:
            if f.permissions and f.permissions[0] == 'l' and (f.link_type is None or f.link_type is FileType.FILE):
                check_path = f.path if getattr(f, 'path', None) else (path + f.name)
                symlink_paths.append(check_path)

        if symlink_paths:
            # Build one script to test all symlinks using shared helper; safely quotes each path
            script = build_test_d_batch_script(symlink_paths)
            cmd = shlex.join(['sh', '-c', script])
            # Даём пропорциональный таймаут: не менее 10с
            sym_timeout = max(10, min(len(symlink_paths) // 2, 20))
            batch_resp = adb.shell(ADBManager.get_device().id, [cmd], timeout=sym_timeout)
            if batch_resp.IsSuccessful and batch_resp.OutputData:
                status = parse_test_d_batch_output(batch_resp.OutputData)

                for f in files:
                    if f.permissions and f.permissions[0] == 'l':
                        p = f.path if getattr(f, 'path', None) else (path + f.name)
                        if p in status:
                            f.link_type = FileType.DIRECTORY if status[p] else FileType.FILE
        return files, response.ErrorData

    @classmethod
    def rename(cls, file: File, name) -> (str, str):
        if name.__contains__('/') or name.__contains__('\\'):
            return None, "Invalid name"

        args = [adb.ShellCommand.MV, file.path, (file.location + name)]
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)])
        return None, response.ErrorData or response.OutputData

    @classmethod
    def open_file(cls, file: File) -> (str, str):
        args = [adb.ShellCommand.CAT, file.path]
        if file.isdir:
            return None, "Can't open. %s is a directory" % file.path
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)])
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def delete(cls, file: File) -> (str, str):
        args = [adb.ShellCommand.RM, file.path]
        if file.isdir:
            args = adb.ShellCommand.RM_DIR_FORCE + [file.path]
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)])
        if not response.IsSuccessful or response.OutputData:
            return None, response.ErrorData or response.OutputData
        return "%s '%s' has been deleted" % ('Folder' if file.isdir else 'File', file.path), None

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

    @staticmethod
    def _remote_file_size(source: str) -> int:
        try:
            command = shlex.join(['stat', '-c', '%s', source])
            response = adb.shell(ADBManager.get_device().id, [command])
            if response.IsSuccessful and response.OutputData:
                return int(response.OutputData.strip())
        except (ValueError, AttributeError, TypeError):
            pass
        return 0

    @staticmethod
    def _poll_download_progress(dest_file, total, callback, name, stop_event):
        # adb pull only prints `[ N%]` progress to a TTY; when its output is
        # piped (as here) it stays silent until the transfer finishes, so the
        # progress bar never moved. Derive progress from the size of the file
        # being written locally instead.
        while not stop_event.wait(0.25):
            try:
                current = os.path.getsize(dest_file)
            except OSError:
                continue
            callback(name, min(int(current * 100 / total), 99))

    @classmethod
    def download(cls, progress_callback: callable, source: str, destination: str) -> (str, str):
        if not destination:
            destination = Settings.device_downloads_path(ADBManager.get_device())
        if ADBManager.get_device() and source and destination:
            helper = cls.UpDownHelper(progress_callback)

            name = source.rstrip('/').rsplit('/', 1)[-1]
            total = cls._remote_file_size(source)
            dest_file = os.path.join(destination, name) if os.path.isdir(destination) else destination
            stop_event = threading.Event()
            if total > 0 and progress_callback:
                threading.Thread(
                    target=cls._poll_download_progress,
                    args=(dest_file, total, progress_callback, name, stop_event),
                    daemon=True,
                ).start()

            response = adb.pull(ADBManager.get_device().id, source, destination, helper.call)
            stop_event.set()
            if response.IsSuccessful and total > 0 and progress_callback:
                progress_callback(name, 100)

            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None

    @classmethod
    def new_folder(cls, name) -> (str, str):
        if not ADBManager.get_device():
            return None, "No device selected!"

        args = [adb.ShellCommand.MKDIR, (ADBManager.path() + name)]
        response = adb.shell(ADBManager.get_device().id, [shlex.join(args)])
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def fetch_exif_thumbnail(cls, device_id: str, path: str):
        """Returns (jpeg_bytes, None) or (None, error_str)"""
        try:
            import piexif
            from app.services.adb import exec_out_head
            raw = exec_out_head(device_id, path)
            if not raw:
                return None, "empty response"
            exif = piexif.load(raw)
            thumb = exif.get("thumbnail")
            if thumb:
                return thumb, None
            return None, "no thumbnail in EXIF"
        except Exception as e:
            return None, str(e)

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> (str, str):
        if ADBManager.get_device() and ADBManager.path() and source:
            helper = cls.UpDownHelper(progress_callback)
            response = adb.push(ADBManager.get_device().id, source, ADBManager.path(), helper.call)
            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None


class StorageRepository:
    """Helpers for device model name, disk usage, and SD card detection."""

    @staticmethod
    def get_device_model(device_id: str) -> str:
        """Return ro.product.model, e.g. 'Pixel 6'."""
        try:
            response = adb.shell(device_id, [shlex.join(adb.ShellCommand.GETPROP_PRODUCT_MODEL)])
            if response.IsSuccessful and response.OutputData:
                return response.OutputData.strip()
        except Exception:
            pass
        return ''

    @staticmethod
    def get_disk_info(device_id: str, path: str = '/sdcard') -> dict:
        """Return {'avail_gb': float, 'total_gb': float} for path, or empty dict on failure.

        Tries `df -k <path>` (POSIX, Android busybox) first; the last data line has
        columns: Filesystem, 1K-blocks, Used, Available, Use%, Mounted-on.
        Falls back to `df <path>` which may give KB or 512-byte blocks depending on busybox."""
        for flag in ['-k', '']:
            try:
                cmd_parts = ['df'] + ([flag] if flag else []) + [path]
                response = adb.shell(device_id, [shlex.join(cmd_parts)])
                if not response.IsSuccessful or not response.OutputData:
                    continue
                lines = [l.strip() for l in response.OutputData.splitlines() if l.strip()]
                # skip header, take last data line (handles line-wrapped output)
                data_lines = [l for l in lines if not l.startswith('Filesystem')]
                if not data_lines:
                    continue
                parts = data_lines[-1].split()
                # expect at least 4 numeric columns after filesystem name
                # handle wrapped: if first line ends with fs name only, parts may be short
                if len(parts) < 4:
                    continue
                # columns: [filesystem, total, used, avail, ...]  (1K-blocks with -k)
                total_kb = int(parts[1])
                avail_kb = int(parts[3])
                if flag == '-k' or total_kb > 1024 * 1024:
                    # values are in KB
                    divisor = 1024 * 1024
                else:
                    # values are in 512-byte blocks (some old busybox without -k)
                    divisor = 2 * 1024 * 1024
                return {
                    'avail_gb': round(avail_kb / divisor, 1),
                    'total_gb': round(total_kb / divisor, 1),
                }
            except Exception:
                continue
        return {}

    @staticmethod
    def get_sd_card_path(device_id: str) -> str:
        """Return /storage/XXXX-XXXX path if external SD card is present, else empty string."""
        import re
        try:
            response = adb.shell(device_id, [shlex.join(['ls', '/storage/'])])
            if response.IsSuccessful and response.OutputData:
                for entry in response.OutputData.split():
                    if re.match(r'^[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}$', entry.strip()):
                        return '/storage/' + entry.strip()
        except Exception:
            pass
        return ''


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
