import pathlib

from services.system import self


class ADBPath:
    Linux = 'lib/adb/linux/adb'
    Windows = 'lib\\adb\\win\\adb.exe'


def adb_path():
    full_path = str(pathlib.Path().resolve())

    if self.get_platform() == self.OSType.Linux:
        if not full_path.endswith('/'):
            full_path += '/'
        return full_path + ADBPath.Linux
    elif self.get_platform() == self.OSType.Windows:
        if not full_path.endswith('\\'):
            full_path += '\\'
        return full_path + ADBPath.Windows
    return ''
