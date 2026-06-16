# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import platform

from PyQt5.QtCore import QFile, QIODevice
from importlib.resources import files

from app.data.models import Device
from app.helpers.tools import Singleton, json_to_dict


class Application(metaclass=Singleton):
    __version__ = '1.4.0'
    __author__ = 'Azat Aldeshov'

    def __init__(self):
        print('─────────────────────────────────')
        print('ADB File Explorer v%s' % self.__version__)
        print('Copyright (C) 2025 %s' % self.__author__)
        print('─────────────────────────────────')
        print('Platform %s' % platform.platform())


class Settings(metaclass=Singleton):
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    filename = str(files('app').joinpath('settings.json'))
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
        if 'adb_core' in cls.data and cls.data['adb_core'] == 'python':
            return 'python'
        return 'external'

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

    style_file_list = str(files('resources.styles').joinpath('file-list.qss'))
    style_device_list = str(files('resources.styles').joinpath('device-list.qss'))

    style_notification = str(files('resources.styles').joinpath('notification.qss'))
    style_file_header = str(files('resources.styles').joinpath('file-header.qss'))
    style_empty_label = str(files('resources.styles').joinpath('empty-label.qss'))
    style_properties_dialog = str(files('resources.styles').joinpath('properties-dialog.qss'))
    style_notification_center = str(files('resources.styles').joinpath('notification-center.qss'))
    style_pathbar_input = str(files('resources.styles').joinpath('pathbar-input.qss'))
    style_pathbar_go_button = str(files('resources.styles').joinpath('pathbar-go-button.qss'))

    icon_logo = str(files('resources.icons').joinpath('logo.svg'))
    icon_link = str(files('resources.icons').joinpath('link.svg'))
    icon_no_link = str(files('resources.icons').joinpath('no_link.svg'))
    icon_phone = str(files('resources.icons').joinpath('phone.svg'))
    icon_phone_unknown = str(files('resources.icons').joinpath('phone_unknown.svg'))
    icon_plus = str(files('resources.icons').joinpath('plus.svg'))
    icon_up = str(files('resources.icons').joinpath('up.svg'))
    icon_arrow = str(files('resources.icons').joinpath('arrow.svg'))
    icon_file = str(files('resources.icons.files').joinpath('file.svg'))
    icon_folder = str(files('resources.icons.files').joinpath('folder.svg'))
    icon_file_unknown = str(files('resources.icons.files').joinpath('file_unknown.svg'))
    icon_link_file = str(files('resources.icons.files').joinpath('link_file.svg'))
    icon_link_folder = str(files('resources.icons.files').joinpath('link_folder.svg'))
    icon_link_file_unknown = str(files('resources.icons.files').joinpath('link_file_unknown.svg'))
    icon_files_upload = str(files('resources.icons.files.actions').joinpath('files_upload.svg'))
    icon_folder_upload = str(files('resources.icons.files.actions').joinpath('folder_upload.svg'))
    icon_folder_create = str(files('resources.icons.files.actions').joinpath('folder_create.svg'))
