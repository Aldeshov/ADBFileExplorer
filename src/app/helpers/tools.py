# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import json
import logging
import os
import shutil
import subprocess
import shlex

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QObject, QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QWidget

from app.data.models import MessageData
from typing import Dict, List

try:
    from adb_shell.auth.keygen import keygen
    from adb_shell.auth.sign_pythonrsa import PythonRSASigner
except ImportError:
    keygen = None
    PythonRSASigner = None

class CommonProcess:
    """
    CommonProcess - executes subprocess then saves output data and exit code.
    If 'stdout_callback' is defined then every output data line will call this function

    Keyword arguments:
    arguments -- array list of arguments
    stdout -- define stdout (default subprocess.PIPE)
    stdout_callback -- callable function, params: (data: str) -> None (default None)
    """

    def __init__(self, arguments: list, stdout=subprocess.PIPE, stdout_callback: callable = None):
        self.ErrorData = None
        self.OutputData = None
        self.IsSuccessful = False
        if arguments:
            try:
                # Merge stderr into stdout so the callback receives both
                stderr_target = subprocess.STDOUT if stdout_callback else subprocess.PIPE
                process = subprocess.Popen(arguments, stdout=stdout, stderr=stderr_target)
                if stdout == subprocess.PIPE and stdout_callback:
                    for line in iter(process.stdout.readline, b''):
                        stdout_callback(line.decode(encoding='utf-8'))
                data, error = process.communicate()
                self.ExitCode = process.poll()
                self.IsSuccessful = self.ExitCode == 0

                decoded_data = data.decode(encoding='utf-8') if data else None
                decoded_error = error.decode(encoding='utf-8') if error else None

                if self.IsSuccessful:
                    self.OutputData = decoded_data or decoded_error
                    self.ErrorData = None
                else:
                    self.ErrorData = decoded_error
                    self.OutputData = decoded_data

            except FileNotFoundError:
                self.ErrorData = "Command '%s' failed! File (command) '%s' not found!" % \
                                 (' '.join(arguments), arguments[0])
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s" % (error, type(error)))
                self.ErrorData = str(error)


class AsyncRepositoryWorker(QThread):
    on_response = QtCore.pyqtSignal(object, object)  # Response : data, error

    def __init__(
            self, worker_id: int, name: str,
            repository_method: callable,
            arguments: tuple, response_callback: callable
    ):
        super(AsyncRepositoryWorker, self).__init__()
        self.on_response.connect(response_callback)
        self.finished.connect(self.close)

        self.__repository_method = repository_method
        self.__arguments = arguments
        self.loading_widget = None
        self.closed = False
        self.id = worker_id
        self.name = name

    def run(self):
        data, error = self.__repository_method(*self.__arguments)
        self.on_response.emit(data, error)

    def close(self):
        if self.loading_widget:
            self.loading_widget.close()
        self.deleteLater()
        self.closed = True

    def set_loading_widget(self, widget: QWidget):
        self.loading_widget = widget

    def update_loading_widget(self, path, progress):
        if self.loading_widget and not self.closed:
            self.loading_widget.update_progress('SOURCE: %s' % path, progress)


class ProgressCallbackHelper(QObject):
    progress_callback = QtCore.pyqtSignal(str, int)

    def setup(self, parent: QObject, callback: callable):
        self.setParent(parent)
        self.progress_callback.connect(callback)


class Communicate(QObject):
    files = QtCore.pyqtSignal()
    devices = QtCore.pyqtSignal()

    up = QtCore.pyqtSignal()
    files__refresh = QtCore.pyqtSignal()
    path_toolbar__refresh = QtCore.pyqtSignal()

    status_bar = QtCore.pyqtSignal(str, int)  # Message, Duration
    notification = QtCore.pyqtSignal(MessageData)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# ------------------------------
# Symlink directory check helpers
# ------------------------------
def build_test_d_batch_script(paths: List[str]) -> str:
    """
    Build a portable shell snippet that tests each provided path with `test -d` and
    prints a tokenized result for robust parsing.

    Output per path:
      DIR:<path>  when test -d succeeds
      FILE:<path> when test -d fails

    Paths are individually shell-quoted to safely handle spaces, quotes, parentheses, etc.
    """
    if not paths:
        return "echo"  # no-op script
    quoted = " ".join(shlex.quote(p) for p in paths)
    script = (
        "for p in " + quoted + "; do "
        "if test -d \"$p\"; then echo DIR:$p; else echo FILE:$p; fi; "
        "done"
    )
    return script


def parse_test_d_batch_output(output: str) -> Dict[str, bool]:
    """
    Parse the output of `build_test_d_batch_script`.

    Returns a mapping path -> is_dir (True if directory, False otherwise).
    """
    status: Dict[str, bool] = {}
    if not output:
        return status
    for line in output.splitlines():
        if line.startswith('DIR:'):
            status[line[4:]] = True
        elif line.startswith('FILE:'):
            status[line[5:]] = False
    return status


def get_python_rsa_keys_signer(rerun=True):
    if keygen is None or PythonRSASigner is None:
        return None

    privkey = os.path.expanduser('~/.android/adbkey')
    if os.path.isfile(privkey):
        with open(privkey) as f:
            private = f.read()
        pubkey = privkey + '.pub'
        if not os.path.isfile(pubkey):
            if shutil.which('ssh-keygen'):
                os.system(f'ssh-keygen -y -f {privkey} > {pubkey}')
            else:
                raise OSError('Could not call ssh-keygen!')
        with open(pubkey) as f:
            public = f.read()
        return PythonRSASigner(public, private)
    elif rerun:
        # Ensure the ~/.android directory exists before generating keys
        path = os.path.expanduser('~/.android')
        if not os.path.isdir(path):
            os.mkdir(path)
        keygen(privkey)
        return get_python_rsa_keys_signer(False)
    return None


def read_string_from_file(path: str):
    file = QFile(path)
    if file.open(QIODevice.ReadOnly | QIODevice.Text):
        text = QTextStream(file).readAll()
        file.close()
        return text
    return str()


def quote_file_name(path: str):
    return '\'' + path + '\''


def json_to_dict(path: str):
    try:
        return dict(json.loads(read_string_from_file(path)))
    except BaseException as exception:
        logging.error('File %s. %s' % (path, exception))
        return dict()
