# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import platform

from PyQt5.QtCore import QFile, QIODevice
from pkg_resources import resource_filename

from app.data.models import Device
from app.helpers.tools import Singleton, json_to_dict


class Application(metaclass=Singleton):
    __version__ = '1.3.0'
    __author__ = 'Azat Aldeshov'

    def __init__(self):
        print('─────────────────────────────────')
        print('ADB File Explorer v%s' % self.__version__)
        print('Copyright (C) 2022 %s' % self.__author__)
        print('─────────────────────────────────')
        print('Platform %s' % platform.platform())


class Settings(metaclass=Singleton):
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    filename = resource_filename('app', 'settings.json')
    data = None

    @classmethod
    def initialize(cls):
        if cls.data is not None:
            return True

        if not os.path.exists(cls.filename):
            print('Settings file not found! Creating one: %s' % cls.filename)
            file = QFile(cls.filename)
            file.open(QIODevice.WriteOnly)
            file.write(b'{}')
            file.close()

        cls.data = json_to_dict(cls.filename)

    @classmethod
    def adb_kill_server_at_exit(cls):
        cls.initialize()
        if 'adb_kill_server_at_exit' in cls.data:
            return bool(cls.data['adb_kill_server_at_exit'])
        return None

    @classmethod
    def adb_path(cls):
        cls.initialize()
        if 'adb_path' in cls.data:
            return str(cls.data['adb_path'])
        return 'adb'

    @classmethod
    def adb_core(cls):
        cls.initialize()
        if 'adb_core' in cls.data and cls.data['adb_core'] == 'external':
            return 'external'
        return 'python'

    @classmethod
    def adb_run_as_root(cls):
        cls.initialize()
        return 'adb_run_as_root' in cls.data and cls.data['adb_run_as_root'] is True

    @classmethod
    def preserve_timestamp(cls):
        cls.initialize()
        return 'preserve_timestamp' in cls.data and cls.data['preserve_timestamp'] is True

    @classmethod
    def device_downloads_path(cls, device: Device) -> str:
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
