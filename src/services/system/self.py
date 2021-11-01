import platform


class OSType:
    Linux = 'Linux'
    Windows = 'Windows'
    Unknown = 'Unknown'


def get_platform():
    if platform.system().startswith(OSType.Linux):
        return OSType.Linux
    elif platform.system().startswith(OSType.Windows):
        return OSType.Windows
    return OSType.Unknown
