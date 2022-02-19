import os
import pathlib
import platform

from services.data.managers import FileManager
from services.data.models import Singleton

OS = (
    'Unknown',
    'Linux',
    'Windows'
)


class Application:
    __metaclass__ = Singleton
    __path__ = pathlib.Path(__file__).parent.resolve()

    DEBUG = True
    VERSION_CODE = 0.4
    VERSION = f'beta v{VERSION_CODE}'

    PLATFORM = \
        OS[1] if platform.platform().startswith(OS[1]) else OS[2] if platform.platform().startswith(OS[2]) else OS[0]

    PATH = __path__ if not DEBUG else str(pathlib.Path(__path__).parent.absolute())


class Settings:
    __metaclass__ = Singleton

    adb__custom_path_enabled = True
    adb__custom_path_value = "adb"


class Resource:
    __metaclass__ = Singleton
    __path__ = f'{Application.PATH}/res'

    logo = f'{__path__}/logo.png'

    icon_exit = f'{__path__}/icons/exit.png'
    icon_connect = f'{__path__}/icons/connect.png'
    icon_disconnect = f'{__path__}/icons/disconnect.png'
    icon_unknown = f'{__path__}/icons/unknown.png'
    icon_phone = f'{__path__}/icons/phone.png'
    icon_plus = f'{__path__}/icons/plus.png'
    icon_up = f'{__path__}/icons/up.png'
    icon_ok = f'{__path__}/icons/ok.png'
    icon_go = f'{__path__}/icons/go.png'
    icon_file = f'{__path__}/icons/files/file.png'
    icon_folder = f'{__path__}/icons/files/folder.png'
    icon_file_unknown = f'{__path__}/icons/files/file_unknown.png'
    icon_link_file = f'{__path__}/icons/files/link_file.png'
    icon_link_folder = f'{__path__}/icons/files/link_folder.png'
    icon_link_file_unknown = f'{__path__}/icons/files/link_file_unknown.png'
    icon_files_upload = f'{__path__}/icons/files/files_upload.png'
    icon_folder_upload = f'{__path__}/icons/files/folder_upload.png'
    icon_folder_create = f'{__path__}/icons/files/folder_create.png'

    anim_loading = f'{__path__}/anim/loading.gif'


class Default:
    __metaclass__ = Singleton

    adb_path = f'{Application.PATH}\\adb.exe' if Application.PLATFORM == OS[2] else f'{Application.PATH}/adb'
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    @staticmethod
    def device_downloads_path():
        if not os.path.isdir(Default.downloads_path):
            os.mkdir(Default.downloads_path)
        if FileManager.get_device():
            downloads_path = os.path.join(
                Default.downloads_path,
                FileManager.get_device().replace(':', ' ')
            )
            if not os.path.isdir(downloads_path):
                os.mkdir(downloads_path)
            return downloads_path
        return Default.downloads_path
