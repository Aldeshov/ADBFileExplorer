from services import config
from services.system import process


class Commands:
    ADB = [f"{config.adb_path()}"]
    SHELL = [f"{config.adb_path()}", "shell"]  # + ARGUMENTS
    CONNECT = [f"{config.adb_path()}", "connect"]  # + DEVICE_ID
    VERSION = [f"{config.adb_path()}", "--version"]
    START_SERVER = [f"{config.adb_path()}", "start-server"]
    KILL_SERVER = [f"{config.adb_path()}", "kill-server"]


def validate():
    return process.call(Commands.VERSION)


@property
def version():
    return process.run(Commands.VERSION)


def start_server():
    return process.run(Commands.START_SERVER)


def kill_server():
    return process.run(Commands.KILL_SERVER)


def connect(device_id: str):
    return process.run(Commands.CONNECT + [f"{device_id}"])


def shell(args: []):
    return process.run(Commands.SHELL + args)
