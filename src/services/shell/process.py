import shlex
import subprocess

from services.data.models import Singleton


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
            return ProcessRunType.SUCCESSFULL
        except KeyboardInterrupt:
            return ProcessRunType.KEYBOARDINTERRUPT
        except FileNotFoundError:
            return ProcessRunType.FILENOTFOUND

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
    def successfull(cls):
        if cls.__process:
            try:
                cls.__process.check_returncode()
                return True
            except subprocess.CalledProcessError:
                return False


class ShellProcessResponse:
    Successfull: bool
    ExitCode: int
    OutputData: str
    ErrorData: str

    def __init__(self, args: list):
        run = ShellProcess.run(args)
        if run == ProcessRunType.SUCCESSFULL:
            self.Successfull = ShellProcess.successfull() is True
            self.ExitCode = ShellProcess.code()

            self.ErrorData = ShellProcess.error()
            self.OutputData = ShellProcess.data()
        elif run == ProcessRunType.FILENOTFOUND:
            self.Successfull = False
            self.ErrorData = 'ADB not Found! Please check adb'
        elif run == ProcessRunType.KEYBOARDINTERRUPT:
            self.Successfull = False
            self.ErrorData = 'Process has been interrupted by keyboard!'
        else:
            self.Successfull = False
            self.ErrorData = 'Unknown Error'


class ProcessRunType:
    UNKNOWN = -1
    SUCCESSFULL = 0
    FILENOTFOUND = 1
    KEYBOARDINTERRUPT = 2
