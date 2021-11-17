from typing import List

from services.data.drivers import get_files, get_file, get_devices, connect, create_folder, \
    download_path__live, upload_path__live
from services.data.managers import FileManager
from services.data.models import File, Device
from services.settings import default_download_path, copy_files_to_temp


class FileRepository:
    @classmethod
    def file(cls, path) -> (File, str):
        return get_file(FileManager.get_device(), path)

    @classmethod
    def files(cls) -> (List[File], str):
        return get_files(FileManager.get_device(), FileManager.path())

    # @classmethod
    # def download(cls, source: str) -> (str, str):
    #     return download_path(FileManager.get_device(), source, default_download_path())
    #
    # @classmethod
    # def download_to(cls, source: str, destination: str) -> (str, str):
    #     return download_path(FileManager.get_device(), source, destination)

    @classmethod
    def download(cls, source: str, async_fun) -> bool:
        return download_path__live(FileManager.get_device(), source, default_download_path(), async_fun)

    @classmethod
    def download_to(cls, source: str, destination: str, async_fun) -> bool:
        return download_path__live(FileManager.get_device(), source, destination, async_fun)

    @classmethod
    def new_folder(cls, name) -> (str, str):
        path = f'{FileManager.path()}/{name}'
        if FileManager.path().endswith('/'):
            path = f'{FileManager.path()}{name}'
        return create_folder(FileManager.get_device(), path)

    # @classmethod
    # def upload_directory(cls, source: str) -> (str, str):
    #     return upload_path(FileManager.get_device(), source, FileManager.path())
    #
    # @classmethod
    # def upload_files(cls, sources: str) -> (str, str):
    #     response_data, response_error = '', ''
    #     for source in sources:
    #         data, error = upload_path(FileManager.get_device(), source, FileManager.path())
    #         if data:
    #             response_data += f'{data}\n'
    #         if error:
    #             response_error += f'{error}\n'
    #     return response_data, response_error

    @classmethod
    def upload_directory(cls, source: str, async_fun) -> bool:
        return upload_path__live(FileManager.get_device(), source, FileManager.path(), async_fun)

    @classmethod
    def upload_files(cls, sources: list, async_fun) -> bool:
        return upload_path__live(FileManager.get_device(), copy_files_to_temp(sources), FileManager.path(), async_fun)


class DeviceRepository:
    @classmethod
    def devices(cls) -> (List[Device], str):
        return get_devices()

    @classmethod
    def connect(cls, device_id) -> (str, str):
        return connect(device_id)
