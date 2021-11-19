import logging
import subprocess
import sys
import threading
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class Process:
    ExitCode: int
    ErrorData: str
    OutputData: str
    Successful: bool = False

    def __init__(self, arguments: list):
        assert arguments, 'No command specified'
        command = arguments[0]
        try:
            process = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.ExitCode = process.returncode
            self.ErrorData = process.stderr.decode(encoding='utf-8')
            self.OutputData = process.stdout.decode(encoding='utf-8')
            self.Successful = self.ExitCode == 0
        except KeyboardInterrupt:
            self.ErrorData = "Process has been interrupted by keyboard!"
        except FileNotFoundError:
            self.ErrorData = f"Command: {command} not found!"
        except BaseException as error:
            logging.exception(error)
            self.ErrorData = f"Unexpected {error=}, {type(error)=}"


class ObservableProcess(QObject):
    __process__: subprocess.Popen
    __completed__ = QtCore.pyqtSignal(int, str)  # ExitCode, ErrorData

    ExitCode: int
    ErrorData: str
    Successful: bool = False
    # OutPutData: str  # Redirect all output to console

    def __init__(self, arguments: list, async_function: typing.Callable):
        super(ObservableProcess, self).__init__()
        assert arguments and async_function, 'No command specified'
        command = arguments[0]
        try:
            self.__completed__.connect(async_function)
            self.__process__ = subprocess.Popen(arguments, stdout=sys.stdout, stderr=subprocess.PIPE)

            # Observe
            threading.Thread(target=self.__observe__).start()
        except FileNotFoundError:
            self.ErrorData = f"Command: {command} not found!"
        except BaseException as error:
            logging.exception(error)
            self.ErrorData = f"Unexpected {error=}, {type(error)=}"

    def __observe__(self):
        _, error = self.__process__.communicate()
        self.ExitCode = self.__process__.poll()
        self.Successful = self.ExitCode == 0
        self.ErrorData = error.decode(encoding='utf-8')
        self.__completed__.emit(self.ExitCode, self.ErrorData)
