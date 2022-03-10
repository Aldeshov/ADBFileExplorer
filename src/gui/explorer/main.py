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

from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QSizePolicy

from core.main import Adb
from core.managers import Global
from gui.explorer.devices import DeviceHeaderWidget, DeviceListWidget
from gui.explorer.files import FileHeaderWidget, FileListWidget
from gui.explorer.toolbar import UploadTools, ParentButton, PathBar


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

        Global().communicate.files__refresh.connect(print)
        Global().communicate.files__refresh.disconnect()
        Global().communicate.files__refresh.connect(self.__update_files)

    def devices(self):
        self.clear()
        Adb.manager().clear_device()
        self.toolbar = QWidget()

        self.header = DeviceHeaderWidget()
        self.layout.addWidget(self.header)

        self.body = DeviceListWidget(self)
        self.scroll.setWidget(self.body)
        self.layout.addWidget(self.scroll)

    def clear(self):
        self.toolbar.close()
        self.toolbar.deleteLater()
        self.layout.removeWidget(self.toolbar)
        del self.toolbar

        self.header.close()
        self.header.deleteLater()
        self.layout.removeWidget(self.header)
        del self.header

        self.body.close()
        self.body.deleteLater()
        self.layout.removeWidget(self.body)
        del self.body

        self.layout.removeWidget(self.scroll)
        self.scroll.setWidget(None)
