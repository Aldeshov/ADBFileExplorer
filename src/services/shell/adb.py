from services.shell.process import ShellProcessResponse

ADB = 'adb'


class Parameter:
    DEVICE = '-s'
    PULL = 'pull'
    PUSH = 'push'
    SHELL = 'shell'
    CONNECT = 'connect'
    HELP = '--help'
    DEVICES = 'devices'
    START_SERVER = 'start-server'
    KILL_SERVER = 'kill-server'


class ShellCommand:
    LS = 'ls'
    LS_LIST = [LS, '-l']
    LS_VERSION = [LS, '--version']
    LS_FULL_LIST = [LS, '-l', '-a']
    LS_FILE_INFO = [LS, '-l', '-d']

    GETPROP = 'getprop'
    GETPROP_PRODUCT_MODEL = [GETPROP, 'ro.product.model']

    MKDIR = 'mkdir'

    CP = 'cp'

    MV = 'mv'


def validate():
    validation = version().Successfull
    message = "ADB not found!"
    assert validation, message


def version():
    args = [ADB, Parameter.HELP]
    return ShellProcessResponse(args)


def devices():
    args = [ADB, Parameter.DEVICES]
    return ShellProcessResponse(args)


def start_server():
    args = [ADB, Parameter.START_SERVER]
    return ShellProcessResponse(args)


def kill_server():
    args = [ADB, Parameter.KILL_SERVER]
    return ShellProcessResponse(args)


def connect(device_id: str):
    args = [ADB, Parameter.CONNECT, device_id]
    return ShellProcessResponse(args)


def pull(device_id: str, source_path: str, destination_path: str):
    args = [ADB, Parameter.DEVICE, device_id, Parameter.PULL, source_path, destination_path]
    return ShellProcessResponse(args)


def push(device_id: str, source_path: str, destination_path: str):
    args = [ADB, Parameter.DEVICE, device_id, Parameter.PUSH, source_path, destination_path]
    return ShellProcessResponse(args)


def shell(device_id: str, args: list):
    args = [ADB, Parameter.DEVICE, device_id, Parameter.SHELL] + args
    return ShellProcessResponse(args)


def file_list(device_id: str, path: str):
    args = [ADB, Parameter.DEVICE, device_id, ShellCommand.LS, path]
    return ShellProcessResponse(args)
