from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QToolBar, QAction, QFileDialog

from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget
from services.filesystem.config import Asset
from services.manager import FileManager
from services.models import Single


class FileExplorerToolbar(QToolBar):
    def __init__(self, statusbar):
        super(FileExplorerToolbar, self).__init__()
        self.statusbar = statusbar

        plus = QAction(QIcon(Asset.icon_plus), 'Push file', self)
        plus.triggered.connect(self.__action_get_file)
        plus.setShortcut('Ctrl+F')
        self.addAction(plus)

        self.addSeparator()

        up = QAction(QIcon(Asset.icon_up), 'Parent directory', self)
        up.triggered.connect(self.__action_go_to_parent)
        up.setShortcut('Escape')
        self.addAction(up)

    def __action_get_file(self):
        name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        try:
            if not name:
                self.statusbar.message('INFO', 'File not selected')
        except FileNotFoundError:
            self.statusbar.message('ERROR', 'File not found')

    @staticmethod
    def __action_go_to_parent():
        if FileManager.up():
            Single().communicate.refresh.emit()


class Explorer(QWidget):
    def __init__(self, statusbar):
        super().__init__()
        self.statusbar = statusbar
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.body = None
        self.header = None
        self.toolbar = None
        self.scroll = QScrollArea(self)
        self.scroll.setLineWidth(self.width())
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        Single().communicate.files.connect(self.files)
        Single().communicate.devices.connect(self.devices)

    def files(self):
        self.clear()
        self.toolbar = FileExplorerToolbar(self.statusbar)
        self.header = FileHeaderWidget()
        self.header.setMaximumHeight(24)
        self.body = FileListWidget()
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll)

        Single().communicate.refresh.connect(self.scroll.widget().update)

    def devices(self):
        self.clear()
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
