import platform

VERSION = '0.20'


class OS:
    Linux = 'Linux'
    Windows = 'Windows'
    Unknown = 'Unknown'


class ADB:
    Linux = 'bin/adb'
    Windows = 'bin\\adb.exe'

    @classmethod
    def path(cls):
        if platform.system().startswith(OS.Linux):
            return str(cls.Linux)
        elif platform.system().startswith(OS.Windows):
            return str(cls.Windows)
        return 'adb'


class Asset:
    logo = 'assets/logo.png'

    icon_exit = 'assets/icons/exit.png'
    icon_connect = 'assets/icons/connect.png'
    icon_unknown = 'assets/icons/unknown.png'
    icon_phone = 'assets/icons/phone.png'
    icon_plus = 'assets/icons/plus.png'
    icon_up = 'assets/icons/up.png'

    icon_file = 'assets/icons/files/file.png'
    icon_folder = 'assets/icons/files/folder.png'
    icon_file_unknown = 'assets/icons/files/file_unknown.png'
    icon_link_file = 'assets/icons/files/link_file.png'
    icon_link_folder = 'assets/icons/files/link_folder.png'
    icon_link_file_unknown = 'assets/icons/files/link_file_unknown.png'
    icon_link_file_universal = 'assets/icons/files/link_file_universal.png'
