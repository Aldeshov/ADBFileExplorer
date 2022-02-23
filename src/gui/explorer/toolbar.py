from typing import Optional

from PyQt5.QtGui import QIcon, QFocusEvent
from PyQt5.QtWidgets import QToolButton, QMenu, QWidget, QAction, QFileDialog, QInputDialog, QLineEdit, QHBoxLayout

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import MessageData
from data.repositories import FileRepository
from gui.others.notification import MessageType
from helpers.tools import AsyncRepositoryWorker


class UploadTools(QToolButton):
    def __init__(self, parent):
        super(UploadTools, self).__init__(parent)
        self.menu = QMenu(self)
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
            # TODO("Action: Upload Files")
            pass

    def __action_upload_directory__(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')

        if dir_name:
            # TODO("Action: Upload Directory")
            pass

    def __action_create_folder__(self):
        text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')

        if ok:
            # TODO("Action: Create Folder")
            pass
            # data, error = FileRepository.new_folder(text)
            # if error:
            #     error = f"<span style='color: red; font-weight: 600'> {error} </span>"
            #     Global().communicate.notification.emit(
            #         "Creating folder", error, 15000, MessageType.MESSAGE, 100
            #     )
            # if data:
            #     Global().communicate.notification.emit(
            #         "Creating folder", data, 15000, MessageType.MESSAGE, 100
            #     )
            # Global().communicate.files__refresh.emit()

    class FilesUploader:
        def __init__(self, files: list):
            self.files = files
            self.worker: Optional[AsyncRepositoryWorker] = None

        def upload(self, files: list):
            # TODO("Action: Upload Method")
            # Global().communicate.files__refresh.emit()
            pass


class ParentButton(QToolButton):
    def __init__(self, parent):
        super(ParentButton, self).__init__(parent)
        self.parent_action = QAction(QIcon(Resource.icon_up), 'Parent', self)
        self.parent_action.triggered.connect(self.__action__)
        self.parent_action.setShortcut('Escape')
        self.setDefaultAction(self.parent_action)

    @staticmethod
    def __action__():
        if Adb.manager().up():
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
            Global().communicate.notification.emit(
                MessageData(
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> Cannot open location </span>",
                    timeout=10000,
                    message_type=MessageType.MESSAGE,
                    height=80
                )
            )
