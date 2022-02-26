from core.configurations import Settings, Default
from helpers.tools import CommonProcess

ADB_PATH = Settings.adb__custom_path_value if Settings.adb__custom_path_enabled else Default.adb_path


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
    return version().IsSuccessful


def version():
    return CommonProcess([ADB_PATH, Parameter.VERSION])


def devices():
    return CommonProcess([ADB_PATH, Parameter.DEVICES, Parameter.DEVICES_LONG])


def start_server():
    return CommonProcess([ADB_PATH, Parameter.START_SERVER])


def kill_server():
    return CommonProcess([ADB_PATH, Parameter.KILL_SERVER])


def connect(device_id: str):
    return CommonProcess([ADB_PATH, Parameter.CONNECT, device_id])


def disconnect():
    return CommonProcess([ADB_PATH, Parameter.DISCONNECT])


def pull(device_id: str, source_path: str, destination_path: str, stdout_callback: callable):
    args = [ADB_PATH, Parameter.DEVICE, device_id, Parameter.PULL, source_path, destination_path]
    return CommonProcess(arguments=args, stdout_callback=stdout_callback)


def push(device_id: str, source_path: str, destination_path: str, stdout_callback: callable):
    args = [ADB_PATH, Parameter.DEVICE, device_id, Parameter.PUSH, source_path, destination_path]
    return CommonProcess(arguments=args, stdout_callback=stdout_callback)


def shell(device_id: str, args: list):
    return CommonProcess([ADB_PATH, Parameter.DEVICE, device_id, Parameter.SHELL] + args)


def file_list(device_id: str, path: str):
    return CommonProcess([ADB_PATH, Parameter.DEVICE, device_id, ShellCommand.LS, path])