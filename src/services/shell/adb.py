import typing

from config import Settings, Default
from services.shell.process import Process, ObservableProcess

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
    validation = version().Successful
    message = version().ErrorData
    assert validation, message


def version():
    return Process([__ADB__, Parameter.VERSION])


def devices():
    return Process([__ADB__, Parameter.DEVICES])


def start_server():
    return Process([__ADB__, Parameter.START_SERVER])


def kill_server():
    return Process([__ADB__, Parameter.KILL_SERVER])


def connect(device_id: str):
    return Process([__ADB__, Parameter.CONNECT, device_id])


def disconnect():
    return Process([__ADB__, Parameter.DISCONNECT])


def pull(device_id: str, source_path: str, destination_path: str, async_fun: typing.Callable):
    args = [__ADB__, Parameter.DEVICE, device_id, Parameter.PULL, source_path, destination_path]
    return ObservableProcess(args, async_fun)


def push(device_id: str, source_path: str, destination_path: str, async_fun: typing.Callable):
    args = [__ADB__, Parameter.DEVICE, device_id, Parameter.PUSH, source_path, destination_path]
    return ObservableProcess(args, async_fun)


def shell(device_id: str, args: list):
    return Process([__ADB__, Parameter.DEVICE, device_id, Parameter.SHELL] + args)


def file_list(device_id: str, path: str):
    return Process([__ADB__, Parameter.DEVICE, device_id, ShellCommand.LS, path])
