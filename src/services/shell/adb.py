from services.filesystem import process, config
from services.filesystem.live import LiveProcess
from services.shell import ls

ADB = config.ADB.path()


class Parameter:
    DEVICE = "-s"
    PULL = 'pull'
    PUSH = 'push'
    SHELL = "shell"
    CONNECT = "connect"
    VERSION = "--version"
    DEVICES = "devices"
    START_SERVER = "start-server"
    KILL_SERVER = "kill-server"


def validate():
    command = [ADB, Parameter.VERSION]
    validation = process.call(command)
    message = "adb not found!\nPlease check 'bin' folder or replace necessary adb files to 'bin/'"
    assert validation, message


def version():
    command = [ADB, Parameter.VERSION]
    return process.run(command)


def devices():
    command = [ADB, Parameter.DEVICES]
    return process.run(command)


def start_server():
    command = [ADB, Parameter.START_SERVER]
    return process.run(command)


def kill_server():
    command = [ADB, Parameter.KILL_SERVER]
    return process.run(command)


def connect(device_id: str):
    command = [ADB, Parameter.CONNECT, device_id]
    return process.run(command)


def pull(device_id: str, source: str, destination: str):
    command = [ADB, Parameter.DEVICE, device_id, Parameter.PULL, source, destination]
    return process.run(command)


def push(device_id: str, source: str, destination: str):
    command = [ADB, Parameter.DEVICE, device_id, Parameter.PUSH, source, destination]
    return process.run(command)


def shell(device_id: str, args: []):
    command = [ADB, Parameter.DEVICE, device_id, Parameter.SHELL] + args
    return process.run(command)


def file_list(device_id: str, path: str):
    command = [ADB, Parameter.DEVICE, device_id, ls.LS, path]
    return process.run(command)
