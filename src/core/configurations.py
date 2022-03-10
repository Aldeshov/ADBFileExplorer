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

import os
import pathlib
import platform

from PyQt5.QtCore import QFile, QIODevice, QTextStream

from data.models import Device
from helpers.tools import Singleton


class Application:
    __version__ = '1.1.0'
    __metaclass__ = Singleton

    def __init__(self):
        print(Application.NOTICE)

    NOTICE = f"""\033[0;32m
        ADB File Explorer v{__version__} Copyright (C) 2022  Azat Aldeshov
        Platform {platform.platform()}
        This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
        This is free software, and you are welcome to redistribute it
        under certain conditions; type `show c' for details.
    \033[0m"""

    PATH = pathlib.Path(__file__).parent.parent.parent.resolve()


class Defaults:
    __metaclass__ = Singleton

    adb_path = os.path.join(Application.PATH, "adb")
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    @staticmethod
    def device_downloads_path(device: Device) -> str:
        if not os.path.isdir(Defaults.downloads_path):
            os.mkdir(Defaults.downloads_path)
        if device:
            downloads_path = os.path.join(Defaults.downloads_path, device.name)
            if not os.path.isdir(downloads_path):
                os.mkdir(downloads_path)
            return downloads_path
        return Defaults.downloads_path


class Settings(Defaults):
    adb__custom_path_enabled = True
    adb__custom_path_value = "adb"


class Resources:
    __metaclass__ = Singleton

    path = os.path.join(Application.PATH, 'res')

    style_window = os.path.join(path, 'styles', 'window.qss')
    style_notification_button = os.path.join(path, 'styles', 'notification-button.qss')

    icon_logo = os.path.join(path, 'icons', 'logo.svg')
    icon_link = os.path.join(path, 'icons', 'link.svg')
    icon_no_link = os.path.join(path, 'icons', 'no_link.svg')
    icon_close = os.path.join(path, 'icons', 'close.svg')
    icon_phone = os.path.join(path, 'icons', 'phone.svg')
    icon_phone_unknown = os.path.join(path, 'icons', 'phone_unknown.svg')
    icon_plus = os.path.join(path, 'icons', 'plus.svg')
    icon_up = os.path.join(path, 'icons', 'up.svg')
    icon_arrow = os.path.join(path, 'icons', 'arrow.svg')
    icon_file = os.path.join(path, 'icons', 'files', 'file.svg')
    icon_folder = os.path.join(path, 'icons', 'files', 'folder.svg')
    icon_file_unknown = os.path.join(path, 'icons', 'files', 'file_unknown.svg')
    icon_link_file = os.path.join(path, 'icons', 'files', 'link_file.svg')
    icon_link_folder = os.path.join(path, 'icons', 'files', 'link_folder.svg')
    icon_link_file_unknown = os.path.join(path, 'icons', 'files', 'link_file_unknown.svg')
    icon_files_upload = os.path.join(path, 'icons', 'files', 'actions', 'files_upload.svg')
    icon_folder_upload = os.path.join(path, 'icons', 'files', 'actions', 'folder_upload.svg')
    icon_folder_create = os.path.join(path, 'icons', 'files', 'actions', 'folder_create.svg')

    anim_loading = os.path.join(path, 'anim', 'loading.gif')

    @staticmethod
    def read_string_from_file(path: str):
        file = QFile(path)
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            text = QTextStream(file).readAll()
            file.close()
            return text
        return ''
