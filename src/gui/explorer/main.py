from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QFileDialog, QHBoxLayout, QPushButton, \
    QComboBox, QLineEdit, QSizePolicy, QInputDialog

from gui.abstract.base import BaseResponsePopup
from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget
from config import Asset
from services.data.managers import FileManager
from services.data.models import Global
from services.data.repositories import FileRepository


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
        self.upload.addItem(QIcon(Asset.icon_plus), 'Upload...')
        self.upload.addItem(self.Action.upload_files)
        self.upload.addItem(self.Action.upload_directory)
        self.upload.addItem(self.Action.create_folder)
        self.upload.activated[str].connect(self.__action_upload)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(2)
        self.upload.setSizePolicy(policy)
        self.layout.addWidget(self.upload)

        self.parent_dir = QPushButton(QIcon(Asset.icon_up), None, self)
        self.parent_dir.clicked.connect(self.__action_go_to_parent)
        self.parent_dir.setShortcut('Escape')
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        self.parent_dir.setSizePolicy(policy)
        self.layout.addWidget(self.parent_dir)

        self.path = QLineEdit(self)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(8)
        self.path.setSizePolicy(policy)
        self.layout.addWidget(self.path)
        Global().communicate.pathtoolbar__refresh.connect(self.__update_path)

        self.go = QPushButton(QIcon(Asset.icon_ok), None, self)
        self.go.clicked.connect(self.__action_go)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        self.parent_dir.setSizePolicy(policy)
        self.layout.addWidget(self.go)

    def __update_path(self):
        self.path.setText(f"{FileManager.get_device()}:{FileManager.path()}")

    def __action_go(self):
        print(self.path.text())

    def __action_upload(self, item):
        if item == self.Action.upload_files:
            self.explorer.mainwindow.statusBar().showMessage('Files uploading... Please wait')
            file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]
            self.explorer.mainwindow.statusBar().showMessage('Files not selected')

            if file_names:
                response = FileRepository.upload_files(file_names)
                self.show_response_status(response, 'Upload files')

                Global().communicate.files__refresh.emit()
                self.explorer.mainwindow.statusBar().showMessage('Done')

        elif item == self.Action.upload_directory:
            self.explorer.mainwindow.statusBar().showMessage('Directory uploading... Please wait')
            dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')
            self.explorer.mainwindow.statusBar().showMessage('Directory not selected')

            if dir_name:
                response = FileRepository.upload_directory(dir_name)
                self.show_response_status(response, 'Upload directory')

                Global().communicate.files__refresh.emit()
                self.explorer.mainwindow.statusBar().showMessage('Done')

        elif item == self.Action.create_folder:
            self.explorer.mainwindow.statusBar().showMessage('Creating folder...')
            text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')
            if ok:
                response = FileRepository.new_folder(text)
                self.show_response_status(response, 'New folder')

                Global().communicate.files__refresh.emit()
                self.explorer.mainwindow.statusBar().showMessage('Done')

        self.upload.setCurrentIndex(0)

    @staticmethod
    def __action_go_to_parent():
        if FileManager.up():
            Global().communicate.files__refresh.emit()


class Explorer(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.body = None
        self.header = None
        self.toolbar = None
        self.scroll = QScrollArea(self)
        self.scroll.setLineWidth(self.width())
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        Global().communicate.files.connect(self.files)
        Global().communicate.devices.connect(self.devices)

    def __update_files(self):
        self.scroll.widget().update()
        Global().communicate.pathtoolbar__refresh.emit()

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
