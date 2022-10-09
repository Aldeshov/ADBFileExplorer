# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from app.core.main import Adb
from app.core.managers import Global
from app.gui.explorer.devices import DeviceExplorerWidget
from app.gui.explorer.files import FileExplorerWidget


class MainExplorer(QWidget):
    def __init__(self, parent=None):
        super(MainExplorer, self).__init__(parent)
        self.setLayout(QVBoxLayout(self))
        self.body = QWidget(self)

        Global().communicate.files.connect(self.files)
        Global().communicate.devices.connect(self.devices)

    def files(self):
        self.clear()

        self.body = FileExplorerWidget(self)
        self.layout().addWidget(self.body)
        self.body.update()

    def devices(self):
        self.clear()
        Adb.manager().clear()

        self.body = DeviceExplorerWidget(self)
        self.layout().addWidget(self.body)
        self.body.update()

    def clear(self):
        self.layout().removeWidget(self.body)
        self.body.close()
        self.body.deleteLater()
