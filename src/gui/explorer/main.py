from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QSizePolicy

from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget
from gui.explorer.toolbar import UploadTools, ParentButton, PathBar
from services.data.managers import FileManager, Global


class FileExplorerToolbar(QWidget):
    def __init__(self, parent):
        super(FileExplorerToolbar, self).__init__(parent)
        self.explorer = parent
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.upload = UploadTools(self)
        self.upload.setFixedHeight(32)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        policy.setHorizontalStretch(1)
        self.upload.setSizePolicy(policy)
        self.layout.addWidget(self.upload)

        self.parent_dir = ParentButton(self)
        self.parent_dir.setFixedHeight(32)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        policy.setHorizontalStretch(1)
        self.parent_dir.setSizePolicy(policy)
        self.layout.addWidget(self.parent_dir)

        self.path_bar = PathBar(self)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        policy.setHorizontalStretch(8)
        self.path_bar.setSizePolicy(policy)
        self.layout.addWidget(self.path_bar)


class Explorer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.body = QWidget()
        self.header = QWidget()
        self.toolbar = QWidget()
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)

        Global().communicate.files.connect(self.files)
        Global().communicate.devices.connect(self.devices)

    def __update_files(self):
        self.scroll.widget().update()
        Global().communicate.path_toolbar__refresh.emit()

    def files(self):
        self.clear()
        self.toolbar = FileExplorerToolbar(self)
        self.layout.addWidget(self.toolbar)

        self.header = FileHeaderWidget()
        self.layout.addWidget(self.header)

        self.body = FileListWidget(self)
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.scroll)

        self.scroll.widget().update()
        Global().communicate.files__refresh.connect(self.__update_files)

    def devices(self):
        self.clear()
        FileManager.clear_device()
        self.toolbar = QWidget()

        self.header = DeviceHeaderWidget()
        self.layout.addWidget(self.header)

        self.body = DeviceListWidget()
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.scroll)

    def clear(self):
        self.layout.removeWidget(self.toolbar)
        del self.toolbar

        self.layout.removeWidget(self.header)
        del self.header

        self.layout.removeWidget(self.body)
        del self.body

        self.layout.removeWidget(self.scroll)
        self.scroll.setWidget(None)
