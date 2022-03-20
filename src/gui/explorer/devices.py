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

from typing import List, Any

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QRect, QVariant, QSize
from PyQt5.QtGui import QPalette, QPixmap, QMovie
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, QStyleOptionViewItem, QApplication, \
    QStyle, QListView

from core.configurations import Resources
from core.main import Adb
from core.managers import Global
from data.models import Device, DeviceType, MessageData
from data.repositories import DeviceRepository
from helpers.tools import AsyncRepositoryWorker, read_string_from_file


class DeviceItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        result = super(DeviceItemDelegate, self).sizeHint(option, index)
        result.setHeight(40)
        return result

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        if not index.data():
            return super(DeviceItemDelegate, self).paint(painter, option, index)

        top = option.rect.top()
        bottom = option.rect.height()
        first_start = option.rect.left() + 50
        second_start = option.rect.left() + int(option.rect.width() / 2)
        end = option.rect.width() + option.rect.left()

        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)
        painter.setPen(option.palette.color(QPalette.Normal, QPalette.Text))

        painter.drawText(
            QRect(first_start, top, second_start - first_start - 4, bottom),
            option.displayAlignment, index.data().name
        )

        painter.drawText(
            QRect(second_start, top, end - second_start, bottom),
            Qt.AlignCenter | option.displayAlignment, index.data().id
        )


class DeviceListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[Device] = []

    def clear(self):
        self.beginResetModel()
        self.items.clear()
        self.endResetModel()

    def populate(self, devices: list):
        self.beginResetModel()
        self.items.clear()
        self.items = devices
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.items)

    def icon_path(self, index: QModelIndex = ...):
        return Resources.icon_phone if self.items[index.row()].type == DeviceType.DEVICE \
            else Resources.icon_phone_unknown

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return self.items[index.row()]
        elif role == Qt.DecorationRole:
            return QPixmap(self.icon_path(index)).scaled(32, 32, Qt.KeepAspectRatio)
        return QVariant()


class DeviceExplorerWidget(QWidget):
    DEVICES_WORKER_ID = 200

    def __init__(self, parent=None):
        super(DeviceExplorerWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout(self))

        self.header = QLabel('Connected devices', self)
        self.header.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.header)

        self.list = QListView(self)
        self.model = DeviceListModel(self.list)

        self.list.setSpacing(1)
        self.list.setModel(self.model)
        self.list.clicked.connect(self.open)
        self.list.setItemDelegate(DeviceItemDelegate(self.list))
        self.list.setStyleSheet(read_string_from_file(Resources.style_device_list))
        self.layout().addWidget(self.list)

        self.loading = QLabel(self)
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie(Resources.anim_loading, parent=self.loading)
        self.loading_movie.setScaledSize(QSize(48, 48))
        self.loading.setMovie(self.loading_movie)
        self.layout().addWidget(self.loading)

        self.empty_label = QLabel("No connected devices", self)
        self.empty_label.setAlignment(Qt.AlignTop)
        self.empty_label.setContentsMargins(15, 10, 0, 0)
        self.empty_label.setStyleSheet("color: #969696; border: 1px solid #969696")
        self.layout().addWidget(self.empty_label)

        self.layout().setStretch(self.layout().count() - 1, 1)
        self.layout().setStretch(self.layout().count() - 2, 1)

    def update(self):
        super(DeviceExplorerWidget, self).update()
        worker = AsyncRepositoryWorker(
            name="Devices",
            worker_id=self.DEVICES_WORKER_ID,
            repository_method=DeviceRepository.devices,
            arguments=(),
            response_callback=self._async_response
        )
        if Adb.worker().work(worker):
            # First Setup loading view
            self.model.clear()
            self.list.setHidden(True)
            self.loading.setHidden(False)
            self.empty_label.setHidden(True)
            self.loading_movie.start()

            # Then start async worker
            worker.start()

    @property
    def device(self):
        if self.list and self.list.currentIndex() is not None:
            return self.model.items[self.list.currentIndex().row()]

    def _async_response(self, devices, error):
        self.loading_movie.stop()
        self.loading.setHidden(True)

        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Devices',
                    timeout=15000,
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                )
            )
        if not devices:
            self.empty_label.setHidden(False)
        else:
            self.list.setHidden(False)
            self.model.populate(devices)

    def open(self):
        if self.device.type == DeviceType.DEVICE:
            if Adb.manager().set_device(self.device):
                Global().communicate.files.emit()
            else:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Device',
                        timeout=10000,
                        body=f"Could not open the device {Adb.manager().get_device().name}"
                    )
                )
