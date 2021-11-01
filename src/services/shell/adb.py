import subprocess

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
    try:
        return 0 <= subprocess.Popen(Commands.ADB, stdout=subprocess.PIPE).wait() <= 1
    except FileNotFoundError:
        return False


@property
def version():
    if validate():
        return process.run(Commands.VERSION)
    return False


def start_server():
    if validate():
        return process.run(Commands.START_SERVER)
    return False


def kill_server():
    if validate():
        return process.run(Commands.KILL_SERVER)
    return False


def connect(device_id: str):
    if validate():
        return process.run(Commands.CONNECT + [f"{device_id}"])
    return False


def shell(args: []):
    if validate():
        return process.run(Commands.SHELL + args)
    return False
