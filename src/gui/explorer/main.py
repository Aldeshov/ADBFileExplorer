from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout

from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget


class Explorer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.body = None
        self.header = None
        self.scroll = QScrollArea(self)
        self.scroll.setLineWidth(self.width())
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.devices()

    def files(self):
        self.clear()
        self.header = FileHeaderWidget()
        self.header.setMaximumHeight(24)
        self.body = FileListWidget()
        self.scroll.setWidget(self.body)

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll)

    def devices(self):
        self.clear()
        self.header = DeviceHeaderWidget()
        self.header.setMaximumHeight(24)
        self.body = DeviceListWidget(self)
        self.scroll.setWidget(self.body)

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scroll)

    def clear(self):
        self.layout.removeWidget(self.body)
        self.layout.removeWidget(self.header)
        self.layout.removeWidget(self.scroll)
