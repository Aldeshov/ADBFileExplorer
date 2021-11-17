import shlex
import subprocess
import sys
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from services.data.models import Singleton


class ProcessRunType:
    UNKNOWN = -1
    SUCCESSFUL = 0
    FILE_NOTFOUND = 1
    KEYBOARD_INTERRUPT = 2


class ShellProcess:
    __metaclass__ = Singleton

    __process: subprocess.CompletedProcess = None

    @classmethod
    def run(cls, args: list):
        try:
            args = shlex.join(args)
            cls.__process = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            return ProcessRunType.SUCCESSFUL
        except KeyboardInterrupt:
            return ProcessRunType.KEYBOARD_INTERRUPT
        except FileNotFoundError:
            return ProcessRunType.FILE_NOTFOUND

    @classmethod
    def data(cls):
        if cls.__process and cls.__process.stdout:
            return cls.__process.stdout.decode()

    @classmethod
    def error(cls):
        if cls.__process and cls.__process.stderr:
            return cls.__process.stderr.decode()

    @classmethod
    def code(cls):
        if cls.__process:
            return cls.__process.returncode

    @classmethod
    def successful(cls):
        if cls.__process:
            try:
                cls.__process.check_returncode()
                return True
            except subprocess.CalledProcessError:
                return False


class ShellProcessResponse:
    Successful: bool
    ExitCode: int
    OutputData: str
    ErrorData: str

    def __init__(self, args: list):
        run = ShellProcess.run(args)
        if run == ProcessRunType.SUCCESSFUL:
            self.Successful = ShellProcess.successful() is True
            self.ExitCode = ShellProcess.code()

            self.ErrorData = ShellProcess.error()
            self.OutputData = ShellProcess.data()
        elif run == ProcessRunType.FILE_NOTFOUND:
            self.Successful = False
            self.ErrorData = 'ADB not Found! Please check adb'
        elif run == ProcessRunType.KEYBOARD_INTERRUPT:
            self.Successful = False
            self.ErrorData = 'Process has been interrupted by keyboard!'
        else:
            self.Successful = False
            self.ErrorData = 'Unknown Error'


class LiveShellProcess:
    __metaclass__ = Singleton

    __process: subprocess.Popen

    @classmethod
    def run(cls, args: list):
        try:
            args = shlex.join(args)
            cls.__process = subprocess.Popen(
                args,
                stdout=sys.stdout,
                stderr=subprocess.PIPE,
                shell=True
            )
            return ProcessRunType.SUCCESSFUL
        except FileNotFoundError:
            return ProcessRunType.FILE_NOTFOUND

    @classmethod
    def error(cls):
        if cls.code() is not None and not cls.successful():
            return cls.__process.communicate()[1].decode()

    @classmethod
    def code(cls):
        if cls.__process:
            return cls.__process.poll()

    @classmethod
    def successful(cls):
        return cls.code() == 0


class LiveShellProcessObserver(QObject):
    Running: bool
    ExitCode: int
    ErrorData: str

    __process_completed = QtCore.pyqtSignal(int, str)

    def __init__(self, args: list):
        super(LiveShellProcessObserver, self).__init__()
        run = LiveShellProcess.run(args)
        if run == ProcessRunType.SUCCESSFUL:
            self.Running = True
        elif run == ProcessRunType.FILE_NOTFOUND:
            self.Running = False
            self.ErrorData = 'ADB not Found! Please check adb'
        else:
            self.Running = False
            self.ErrorData = 'Unknown Error'

    def observe(self, async_fun=None) -> bool:
        if async_fun:
            self.__process_completed.connect(async_fun)
        self.ExitCode = LiveShellProcess.code()
        self.ErrorData = LiveShellProcess.error()
        self.Running = self.ExitCode is None

        if self.Running:
            threading.Timer(0.25, self.observe).start()
            return True
        self.__process_completed.emit(self.ExitCode, self.ErrorData)
        return False
