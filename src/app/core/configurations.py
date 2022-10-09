# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import platform

from pkg_resources import resource_filename

from app.data.models import Device
from app.helpers.tools import Singleton, get_settings_file, json_to_dict


class Application:
    __version__ = '1.3.0'
    __author__ = 'Azat Aldeshov'
    __metaclass__ = Singleton

    def __init__(self):
        print('─────────────────────────────────')
        print('ADB File Explorer v%s' % self.__version__)
        print('Copyright (C) 2022 %s' % self.__author__)
        print('─────────────────────────────────')
        print('Platform %s' % platform.platform())


class Settings(metaclass=Singleton):
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    @staticmethod
    def adb_kill_server_at_exit():
        data = json_to_dict(get_settings_file())
        if 'adb_kill_server_at_exit' in data:
            return bool(data['adb_kill_server_at_exit'])
        return None

    @staticmethod
    def adb_path():
        data = json_to_dict(get_settings_file())
        if 'adb_path' in data:
            return str(data['adb_path'])
        return 'adb'

    @staticmethod
    def adb_core():
        data = json_to_dict(get_settings_file())
        if 'adb_core' in data and data['adb_core'] == 'external':
            return 'external'
        return 'python'

    @staticmethod
    def adb_run_as_root():
        data = json_to_dict(get_settings_file())
        return 'adb_run_as_root' in data and data['adb_run_as_root'] is True

    @staticmethod
    def preserve_timestamp():
        data = json_to_dict(get_settings_file())
        return 'preserve_timestamp' in data and data['preserve_timestamp'] is True

    @staticmethod
    def device_downloads_path(device: Device) -> str:
        if not os.path.isdir(Settings.downloads_path):
            os.mkdir(Settings.downloads_path)
        if device:
            downloads_path = os.path.join(Settings.downloads_path, device.name)
            if not os.path.isdir(downloads_path):
                os.mkdir(downloads_path)
            return downloads_path
        return Settings.downloads_path


class Resources:
    __metaclass__ = Singleton

    style_window = resource_filename('resources.styles', 'window.qss')
    style_file_list = resource_filename('resources.styles', 'file-list.qss')
    style_device_list = resource_filename('resources.styles', 'device-list.qss')
    style_notification_button = resource_filename('resources.styles', 'notification-button.qss')

    icon_logo = resource_filename('resources.icons', 'logo.svg')
    icon_link = resource_filename('resources.icons', 'link.svg')
    icon_no_link = resource_filename('resources.icons', 'no_link.svg')
    icon_close = resource_filename('resources.icons', 'close.svg')
    icon_phone = resource_filename('resources.icons', 'phone.svg')
    icon_phone_unknown = resource_filename('resources.icons', 'phone_unknown.svg')
    icon_plus = resource_filename('resources.icons', 'plus.svg')
    icon_up = resource_filename('resources.icons', 'up.svg')
    icon_arrow = resource_filename('resources.icons', 'arrow.svg')
    icon_file = resource_filename('resources.icons.files', 'file.svg')
    icon_folder = resource_filename('resources.icons.files', 'folder.svg')
    icon_file_unknown = resource_filename('resources.icons.files', 'file_unknown.svg')
    icon_link_file = resource_filename('resources.icons.files', 'link_file.svg')
    icon_link_folder = resource_filename('resources.icons.files', 'link_folder.svg')
    icon_link_file_unknown = resource_filename('resources.icons.files', 'link_file_unknown.svg')
    icon_files_upload = resource_filename('resources.icons.files.actions', 'files_upload.svg')
    icon_folder_upload = resource_filename('resources.icons.files.actions', 'folder_upload.svg')
    icon_folder_create = resource_filename('resources.icons.files.actions', 'folder_create.svg')

    anim_loading = resource_filename('resources.anim', 'loading.gif')
