from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFocusEvent
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QFileDialog, QHBoxLayout, QPushButton, \
    QComboBox, QLineEdit, QSizePolicy, QInputDialog, QMessageBox

from gui.abstract.base import BaseResponsePopup
from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget
from config import Resource
from gui.others.additional import LoadingWidget
from services.data.managers import FileManager
from services.data.models import Global
from services.data.repositories import FileRepository


class PathBar(QLineEdit):
    def __init__(self, parent: QWidget = 0):
        super(PathBar, self).__init__(parent)

    def focusInEvent(self, event: QFocusEvent):
        super(PathBar, self).focusInEvent(event)
        self.setText(FileManager.path())


class FileExplorerToolbar(BaseResponsePopup):
    class Action:
        upload_files = 'Upload files'
        upload_directory = 'Upload directory'
        create_folder = 'Create folder'

    def __init__(self, explorer):
        super(FileExplorerToolbar, self).__init__()
        self.explorer = explorer
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.upload = QComboBox(self)
        self.upload.setFixedHeight(32)
        self.upload.addItem(QIcon(Resource.icon_plus), 'Upload...')
        self.upload.addItem(self.Action.upload_files)
        self.upload.addItem(self.Action.upload_directory)
        self.upload.addItem(self.Action.create_folder)
        self.upload.activated[str].connect(self.__action_upload)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(2)
        self.upload.setSizePolicy(policy)
        self.layout.addWidget(self.upload)

        self.parent_dir = QPushButton(QIcon(Resource.icon_up), None, self)
        self.parent_dir.setFixedHeight(32)
        self.parent_dir.clicked.connect(self.__action_go_to_parent)
        self.parent_dir.setShortcut('Escape')
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        self.parent_dir.setSizePolicy(policy)
        # noinspection PyTypeChecker
        # QPushButton is QWidget type
        self.layout.addWidget(self.parent_dir)

        self.path = PathBar(self)
        self.path.setFixedHeight(32)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(8)
        self.path.setSizePolicy(policy)
        self.layout.addWidget(self.path)
        self.path.returnPressed.connect(self.__action_go)
        Global().communicate.path_toolbar__refresh.connect(self.__update_path)

        self.go = QPushButton(QIcon(Resource.icon_go), None, self)
        self.go.setFixedHeight(32)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        self.parent_dir.setSizePolicy(policy)
        self.go.clicked.connect(self.__action_go)
        # noinspection PyTypeChecker
        # QPushButton is QWidget type
        self.layout.addWidget(self.go)

    def __update_path(self):
        self.path.setText(f"{FileManager.get_device()}:{FileManager.path()}")

    def __action_go(self):
        path = self.path.text()
        self.path.clearFocus()
        if path.startswith(f"{FileManager.get_device()}:"):
            path = path.replace(f"{FileManager.get_device()}:", '')

        file, error = FileRepository.file(path)
        if error:
            QMessageBox.critical(self, 'Go to folder', error)
            Global().communicate.path_toolbar__refresh.emit()
        elif file and FileManager.go(file):
            Global().communicate.files__refresh.emit()
        else:
            QMessageBox.critical(self, 'Go to folder', 'Cannot open location')

    def __action_upload(self, item):
        if item == self.Action.upload_files:
            file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]
            self.explorer.main_window.statusBar().showMessage('Files not selected')

            if file_names:
                self.explorer.main_window.statusBar().showMessage('Uploading files...')
                FileRepository.upload_files(file_names, self.__uploaded)
                self.explorer.loading_upload.show()

        elif item == self.Action.upload_directory:
            dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')
            self.explorer.main_window.statusBar().showMessage('Directory not selected')

            if dir_name:
                self.explorer.main_window.statusBar().showMessage('Uploading directory...')
                FileRepository.upload_directory(dir_name, self.__uploaded)
                self.explorer.loading_upload.show()

        elif item == self.Action.create_folder:
            self.explorer.main_window.statusBar().showMessage('Creating folder...')
            text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')

            if ok:
                response = FileRepository.new_folder(text)
                self.show_response_status(response, 'New folder')

                Global().communicate.files__refresh.emit()
                self.explorer.main_window.statusBar().showMessage('Done')

        self.upload.setCurrentIndex(0)

    def __uploaded(self, code, error):
        self.explorer.loading_upload.close()
        if error or code != 0:
            self.show_response_status((None, error or 'Failed to upload! Check the terminal'), 'Upload')
        else:
            self.show_response_status(("Successfully uploaded!", None), 'Upload')
        self.explorer.main_window.statusBar().showMessage('Done')

        Global().communicate.files__refresh.emit()

    @staticmethod
    def __action_go_to_parent():
        if FileManager.up():
            Global().communicate.files__refresh.emit()


class Explorer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.body = None
        self.header = None
        self.toolbar = None
        self.scroll = QScrollArea(self)
        self.scroll.setLineWidth(self.width())
        self.scroll.setWidgetResizable(True)
        self.loading_upload = LoadingWidget(self, 'Uploading...')
        self.loading_download = LoadingWidget(self, 'Downloading...')
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        Global().communicate.files.connect(self.files)
        Global().communicate.devices.connect(self.devices)

    def __update_files(self):
        self.scroll.widget().update()
        Global().communicate.path_toolbar__refresh.emit()

    def files(self):
        self.clear()
        self.toolbar = FileExplorerToolbar(self)
        self.header = FileHeaderWidget()
        self.header.setMaximumHeight(24)
        self.body = FileListWidget(self)
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll)

        Global().communicate.files__refresh.connect(
            self.__update_files
        )

    def devices(self):
        self.clear()
        FileManager.clear_device()
        self.header = DeviceHeaderWidget()
        self.header.setMaximumHeight(24)
        self.body = DeviceListWidget()
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll)

    def clear(self):
        self.layout.removeWidget(self.toolbar)
        self.layout.removeWidget(self.header)
        self.layout.removeWidget(self.body)
        self.layout.removeWidget(self.scroll)
        self.null()

    def null(self):
        self.toolbar = None
        self.header = None
        self.body = None
        self.scroll.setWidget(None)
