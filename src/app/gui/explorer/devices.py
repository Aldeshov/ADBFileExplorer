# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from typing import Any

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QRect, QVariant
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyledItemDelegate, QStyleOptionViewItem, QApplication, \
    QStyle, QListView

from app.core.configurations import Resources
from app.core.main import Adb
from app.core.managers import Global
from app.data.models import DeviceType, MessageData, MessageType
from app.data.repositories import DeviceRepository, StorageRepository
from app.helpers.tools import AsyncRepositoryWorker, read_string_from_file
from app.gui.widgets.circular_progress import CircularProgress


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
        self.items = []

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
        self.main_layout = QVBoxLayout(self)

        self.header = QLabel('Connected devices', self)
        self.header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header)

        self.list = QListView(self)
        self.model = DeviceListModel(self.list)

        self.list.setSpacing(1)
        self.list.setModel(self.model)
        self.list.clicked.connect(self.open)
        self.list.setItemDelegate(DeviceItemDelegate(self.list))
        self.list.setStyleSheet(read_string_from_file(Resources.style_device_list))
        self.main_layout.addWidget(self.list)

        self.loading = CircularProgress(size=48, thickness=3, parent=self)
        self.loading.setVisible(False)
        self.main_layout.addWidget(self.loading, alignment=Qt.AlignCenter)

        self.empty_label = QLabel("No connected devices", self)
        self.empty_label.setAlignment(Qt.AlignTop)
        self.empty_label.setContentsMargins(15, 10, 0, 0)
        self.empty_label.setStyleSheet(read_string_from_file(Resources.style_empty_label))
        self.main_layout.addWidget(self.empty_label)

        self.main_layout.setStretch(self.layout().count() - 1, 1)
        self.main_layout.setStretch(self.layout().count() - 2, 1)
        self.setLayout(self.main_layout)

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
            self.loading.start()

            # Then start async worker
            worker.start()

    @property
    def device(self):
        if self.list and self.list.currentIndex() is not None:
            return self.model.items[self.list.currentIndex().row()]

    def _async_response(self, devices, error):
        self.loading.stop()
        self.loading.setHidden(True)

        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Devices',
                    timeout=15000,
                    body=str(error),
                    message_type=MessageType.ERROR_MESSAGE,
                )
            )
        if not devices:
            self.empty_label.setHidden(False)
        else:
            self.list.setHidden(False)
            self.model.populate(devices)

    def open(self):
        if self.device.id:
            if Adb.manager().set_device(self.device):
                Global().communicate.files.emit()
                # Fetch device info in background and broadcast via signal
                worker = AsyncRepositoryWorker(
                    name="DeviceInfo",
                    worker_id=201,
                    repository_method=self._fetch_device_info,
                    arguments=(self.device.id,),
                    response_callback=self._on_device_info
                )
                if Adb.worker().work(worker):
                    worker.start()
            else:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Device',
                        timeout=10000,
                        body="Could not open the device %s" % Adb.manager().get_device().name
                    )
                )

    @staticmethod
    def _fetch_device_info(device_id: str):
        """Called in background thread — returns (model, avail_gb, total_gb, sd_path)."""
        model = StorageRepository.get_device_model(device_id)
        disk = StorageRepository.get_disk_info(device_id, '/sdcard')
        sd = StorageRepository.get_sd_card_path(device_id)
        avail = disk.get('avail_gb', 0.0)
        total = disk.get('total_gb', 0.0)
        return (model, avail, total, sd), None

    @staticmethod
    def _on_device_info(data, error):
        if data:
            model, avail, total, sd = data
            Global().communicate.device_info_ready.emit(model, float(avail), float(total), sd or '')
