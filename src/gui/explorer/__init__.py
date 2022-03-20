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

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from core.main import Adb
from core.managers import Global
from gui.explorer.devices import DeviceExplorerWidget
from gui.explorer.files import FileExplorerWidget


class MainExplorer(QWidget):
    def __init__(self, parent=None):
        super(MainExplorer, self).__init__(parent)
        self.body = QWidget(self)
        self.setLayout(QVBoxLayout(self))

        Global().communicate.files.connect(self.files)
        Global().communicate.devices.connect(self.devices)

    def files(self):
        self.clear()

        self.body = FileExplorerWidget(self)
        self.layout().addWidget(self.body)
        self.body.update()

    def devices(self):
        self.clear()
        Adb.manager().clear_device()

        self.body = DeviceExplorerWidget(self)
        self.layout().addWidget(self.body)
        self.body.update()

    def clear(self):
        self.layout().removeWidget(self.body)
        self.body.close()
        self.body.deleteLater()
