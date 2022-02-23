from core.configurations import Settings, Default
from helpers.tools import CommonProcess

__ADB__ = Settings.adb__custom_path_value if Settings.adb__custom_path_enabled else Default.adb_path


class Parameter:
    DEVICE = '-s'
    PULL = 'pull'
    PUSH = 'push'
    SHELL = 'shell'
    CONNECT = 'connect'
    HELP = '--help'
    VERSION = '--version'
    DEVICES = 'devices'
    DEVICES_LONG = '-l'
    DISCONNECT = 'disconnect'
    START_SERVER = 'start-server'
    KILL_SERVER = 'kill-server'


class ShellCommand:
    LS = 'ls'
    LS_ALL = [LS, '-a']
    LS_DIRS = [LS, '-d']
    LS_LIST = [LS, '-l']
    LS_LIST_DIRS = [LS, '-l', '-d']
    LS_ALL_DIRS = [LS, '-a', '-d']
    LS_ALL_LIST = [LS, '-a', '-l']
    LS_ALL_LIST_DIRS = [LS, '-a', '-l', '-d']
    LS_VERSION = [LS, '--version']

    GETPROP = 'getprop'
    GETPROP_PRODUCT_MODEL = [GETPROP, 'ro.product.model']

    MKDIR = 'mkdir'


def validate():
    validation = version().IsSuccessful
    message = version().ErrorData
    assert validation, message


def version():
    return CommonProcess([__ADB__, Parameter.VERSION])


def devices():
    return CommonProcess([__ADB__, Parameter.DEVICES, Parameter.DEVICES_LONG])


def start_server():
    return CommonProcess([__ADB__, Parameter.START_SERVER])


def kill_server():
    return CommonProcess([__ADB__, Parameter.KILL_SERVER])


def connect(device_id: str):
    return CommonProcess([__ADB__, Parameter.CONNECT, device_id])


def disconnect():
    return CommonProcess([__ADB__, Parameter.DISCONNECT])


def pull(device_id: str, source_path: str, destination_path: str):
    return CommonProcess([__ADB__, Parameter.DEVICE, device_id, Parameter.PULL, source_path, destination_path], None)


def push(device_id: str, source_path: str, destination_path: str):
    return CommonProcess([__ADB__, Parameter.DEVICE, device_id, Parameter.PUSH, source_path, destination_path], None)


def shell(device_id: str, args: list):
    return CommonProcess([__ADB__, Parameter.DEVICE, device_id, Parameter.SHELL] + args)


def file_list(device_id: str, path: str):
    return CommonProcess([__ADB__, Parameter.DEVICE, device_id, ShellCommand.LS, path])
