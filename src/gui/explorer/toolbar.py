# ADB File Explorer `tool`
# Copyright (C) 2022  Azat Aldeshov azata1919@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtGui import QIcon, QFocusEvent
from PyQt5.QtWidgets import QToolButton, QMenu, QWidget, QAction, QFileDialog, QInputDialog, QLineEdit, QHBoxLayout

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import MessageData, MessageType
from data.repositories import FileRepository
from gui.explorer.files import FileListWidget
from helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper


class UploadTools(QToolButton):
    def __init__(self, parent):
        super(UploadTools, self).__init__(parent)
        self.menu = QMenu(self)
        self.uploader = self.FilesUploader()
        self.show_action = QAction(QIcon(Resource.icon_plus), 'Upload', self)
        self.show_action.triggered.connect(self.showMenu)
        self.setDefaultAction(self.show_action)

        upload_files = QAction(QIcon(Resource.icon_files_upload), '&Upload files', self)
        upload_files.triggered.connect(self.__action_upload_files__)
        self.menu.addAction(upload_files)

        upload_directory = QAction(QIcon(Resource.icon_folder_upload), '&Upload directory', self)
        upload_directory.triggered.connect(self.__action_upload_directory__)
        self.menu.addAction(upload_directory)

        upload_files = QAction(QIcon(Resource.icon_folder_create), '&Create folder', self)
        upload_files.triggered.connect(self.__action_create_folder__)
        self.menu.addAction(upload_files)
        self.setMenu(self.menu)

    def __action_upload_files__(self):
        file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]

        if file_names:
            self.uploader.setup(file_names)
            self.uploader.upload()

    def __action_upload_directory__(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')

        if dir_name:
            self.uploader.setup([dir_name])
            self.uploader.upload()

    def __action_create_folder__(self):
        text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')

        if ok and text:
            data, error = FileRepository.new_folder(text)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title="Creating folder",
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                        timeout=15000,
                        message_type=MessageType.MESSAGE,
                        height=100
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title="Creating folder",
                        body=data,
                        timeout=15000,
                        message_type=MessageType.MESSAGE,
                        height=100
                    )
                )
            Global().communicate.files__refresh.emit()

    class FilesUploader:
        UPLOAD_WORKER_ID = 398

        def __init__(self):
            self.files = []

        def setup(self, files: list):
            self.files = files

        def upload(self, data=None, error=None):
            if self.files:
                helper = ProgressCallbackHelper()
                worker = AsyncRepositoryWorker(
                    worker_id=self.UPLOAD_WORKER_ID,
                    name="Upload",
                    repository_method=FileRepository.upload,
                    response_callback=self.upload,
                    arguments=(helper.progress_callback.emit, self.files.pop())
                )
                if Adb.worker().work(worker):
                    Global().communicate.notification.emit(
                        MessageData(
                            title="Uploading",
                            body="Uploading",
                            message_type=MessageType.LOADING_MESSAGE,
                            message_catcher=worker.set_loading_widget
                        )
                    )
                    helper.setup(worker, worker.update_loading_widget)
                    worker.loading_widget.setup_progress()
                    worker.start()
            else:
                Global().communicate.files__refresh.emit()

            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Upload error',
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                        timeout=15000,
                        message_type=MessageType.MESSAGE,
                        height=100
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Uploaded',
                        body=data,
                        timeout=15000,
                        message_type=MessageType.MESSAGE
                    )
                )


class ParentButton(QToolButton):
    def __init__(self, parent):
        super(ParentButton, self).__init__(parent)
        self.parent_action = QAction(QIcon(Resource.icon_up), 'Parent', self)
        self.parent_action.triggered.connect(self.__action__)
        self.parent_action.setShortcut('Escape')
        self.setDefaultAction(self.parent_action)

    @staticmethod
    def __action__():
        if Adb.worker().check(FileListWidget.FILES_WORKER_ID) and Adb.manager().up():
            Global().communicate.files__refresh.emit()


class PathBar(QWidget):
    class LineEdit(QLineEdit):
        def focusInEvent(self, event: QFocusEvent):
            super().focusInEvent(event)
            self.setText(Adb.manager().path())

    def __init__(self, parent: QWidget = 0):
        super(PathBar, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.path_text = self.LineEdit()
        self.path_text.setFixedHeight(32)
        self.path_text.setText(f"{Adb.manager().get_device().name}:/")
        self.path_text.returnPressed.connect(self.__action__)
        self.layout.addWidget(self.path_text)
        self.path_go = QToolButton()
        self.path_go.setFixedHeight(32)
        self.path_go.setFixedWidth(32)
        self.action = QAction(QIcon(Resource.icon_go), 'Go', self)
        self.action.triggered.connect(self.__action__)
        self.path_go.setDefaultAction(self.action)
        self.layout.addWidget(self.path_go)

        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        Global().communicate.path_toolbar__refresh.connect(self.__update__)

    def __update__(self):
        self.path_text.setText(f"{Adb.manager().get_device().name}:{Adb.manager().path()}")

    def __action__(self):
        path = self.path_text.text()
        self.path_text.clearFocus()
        if path.startswith(f"{Adb.manager().get_device().name}:"):
            path = path.replace(f"{Adb.manager().get_device().name}:", '')

        file, error = FileRepository.file(path)
        if error:
            Global().communicate.path_toolbar__refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    title="Opening folder",
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    timeout=10000,
                    message_type=MessageType.MESSAGE,
                    height=100
                )
            )
        elif file and Adb.manager().go(file):
            Global().communicate.files__refresh.emit()
        else:
            Global().communicate.path_toolbar__refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> Cannot open location </span>",
                    timeout=10000,
                    message_type=MessageType.MESSAGE,
                    height=80
                )
            )
