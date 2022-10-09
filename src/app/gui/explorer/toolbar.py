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

from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QMenu, QWidget, QAction, QFileDialog, QInputDialog, QLineEdit, QHBoxLayout

from app.core.configurations import Resources
from app.core.main import Adb
from app.core.managers import Global
from app.data.models import MessageData, MessageType
from app.data.repositories import FileRepository
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper


class UploadTools(QToolButton):
    def __init__(self, parent):
        super(UploadTools, self).__init__(parent)
        self.menu = QMenu(self)
        self.uploader = self.FilesUploader()

        self.show_action = QAction(QIcon(Resources.icon_plus), 'Upload', self)
        self.show_action.triggered.connect(self.showMenu)
        self.setDefaultAction(self.show_action)

        upload_files = QAction(QIcon(Resources.icon_files_upload), '&Upload files', self)
        upload_files.triggered.connect(self.__action_upload_files__)
        self.menu.addAction(upload_files)

        upload_directory = QAction(QIcon(Resources.icon_folder_upload), '&Upload directory', self)
        upload_directory.triggered.connect(self.__action_upload_directory__)
        self.menu.addAction(upload_directory)

        upload_files = QAction(QIcon(Resources.icon_folder_create), '&Create folder', self)
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
                        timeout=15000,
                        title="Creating folder",
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title="Creating folder",
                        timeout=15000,
                        body=data,
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
                            message_type=MessageType.LOADING_MESSAGE,
                            message_catcher=worker.set_loading_widget
                        )
                    )
                    helper.setup(worker, worker.update_loading_widget)
                    worker.start()
            else:
                Global().communicate.files__refresh.emit()

            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        timeout=15000,
                        title='Upload error',
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Uploaded',
                        timeout=15000,
                        body=data,
                    )
                )


class ParentButton(QToolButton):
    def __init__(self, parent):
        super(ParentButton, self).__init__(parent)
        self.action = QAction(QIcon(Resources.icon_up), 'Parent', self)
        self.action.setShortcut('Escape')
        self.action.triggered.connect(
            lambda: Global().communicate.files__refresh.emit() if Adb.worker().check(300) and Adb.manager().up() else ''
        )
        self.setDefaultAction(self.action)


class PathBar(QWidget):
    def __init__(self, parent: QWidget):
        super(PathBar, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))

        self.prefix = Adb.manager().get_device().name + ":"
        self.value = Adb.manager().path()

        self.text = QLineEdit(self)
        self.text.installEventFilter(self)
        self.text.setStyleSheet("padding: 5;")
        self.text.setText(self.prefix + self.value)
        self.text.textEdited.connect(self._update)
        self.text.returnPressed.connect(self._action)
        self.layout().addWidget(self.text)

        self.go = QToolButton(self)
        self.go.setStyleSheet("padding: 4;")
        self.action = QAction(QIcon(Resources.icon_arrow), 'Go', self)
        self.action.triggered.connect(self._action)
        self.go.setDefaultAction(self.action)
        self.layout().addWidget(self.go)

        self.layout().setContentsMargins(0, 0, 0, 0)
        Global().communicate.path_toolbar__refresh.connect(self._clear)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if obj == self.text and event.type() == QEvent.FocusIn:
            self.text.setText(self.value)
        elif obj == self.text and event.type() == QEvent.FocusOut:
            self.text.setText(self.prefix + self.value)
        return super(PathBar, self).eventFilter(obj, event)

    def _clear(self):
        self.value = Adb.manager().path()
        self.text.setText(self.prefix + self.value)

    def _update(self, text: str):
        self.value = text

    def _action(self):
        self.text.clearFocus()
        file, error = FileRepository.file(self.value)
        if error:
            Global().communicate.path_toolbar__refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=10000,
                    title="Opening folder",
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                )
            )
        elif file and Adb.manager().go(file):
            Global().communicate.files__refresh.emit()
        else:
            Global().communicate.path_toolbar__refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=10000,
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> Cannot open location </span>",
                )
            )
