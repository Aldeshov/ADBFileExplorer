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

from data.models import Device
from helpers.tools import Singleton


class Application:
    __version__ = '1.0.0'
    __metaclass__ = Singleton

    NOTICE = f"""\033[0;32m
        ADB File Explorer v{__version__} Copyright (C) 2022  Azat Aldeshov
        Platform {platform.platform()}
        This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
        This is free software, and you are welcome to redistribute it
        under certain conditions; type `show c' for details.
    \033[0m"""

    PATH = pathlib.Path(__file__).parent.parent.parent.resolve()


class Default:
    __metaclass__ = Singleton

    adb_path = os.path.join(Application.PATH, "adb")
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    @staticmethod
    def device_downloads_path(device: Device) -> str:
        if not os.path.isdir(Default.downloads_path):
            os.mkdir(Default.downloads_path)
        if device:
            downloads_path = os.path.join(Default.downloads_path, device.name)
            if not os.path.isdir(downloads_path):
                os.mkdir(downloads_path)
            return downloads_path
        return Default.downloads_path


class Settings(Default):
    adb__custom_path_enabled = True
    adb__custom_path_value = "adb"


class Resource:
    __metaclass__ = Singleton

    path = os.path.join(Application.PATH, 'res')

    logo = os.path.join(path, 'icons', 'logo.png')
    icon_exit = os.path.join(path, 'icons', 'exit.png')
    icon_connect = os.path.join(path, 'icons', 'connect.png')
    icon_disconnect = os.path.join(path, 'icons', 'disconnect.png')
    icon_unknown = os.path.join(path, 'icons', 'unknown.png')
    icon_phone = os.path.join(path, 'icons', 'phone.png')
    icon_plus = os.path.join(path, 'icons', 'plus.png')
    icon_up = os.path.join(path, 'icons', 'up.png')
    icon_ok = os.path.join(path, 'icons', 'ok.png')
    icon_go = os.path.join(path, 'icons', 'go.png')
    icon_file = os.path.join(path, 'icons', 'files', 'file.svg')
    icon_folder = os.path.join(path, 'icons', 'files', 'folder.png')
    icon_file_unknown = os.path.join(path, 'icons', 'files', 'file_unknown.png')
    icon_link_file = os.path.join(path, 'icons', 'files', 'link_file.svg')
    icon_link_folder = os.path.join(path, 'icons', 'files', 'link_folder.png')
    icon_link_file_unknown = os.path.join(path, 'icons', 'files', 'link_file_unknown.png')
    icon_files_upload = os.path.join(path, 'icons', 'files', 'files_upload.png')
    icon_folder_upload = os.path.join(path, 'icons', 'files', 'folder_upload.png')
    icon_folder_create = os.path.join(path, 'icons', 'files', 'folder_create.png')
    anim_loading = os.path.join(path, 'anim', 'loading.gif')

    icon_close = os.path.join(path, 'icons', 'close.svg')
