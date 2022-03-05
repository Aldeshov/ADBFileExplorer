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

from PyQt5.QtCore import Qt

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import Device, DeviceType, MessageData, MessageType
from helpers.tools import AsyncRepositoryWorker
from data.repositories import DeviceRepository
from gui.abstract.base import BaseListWidget, BaseListItemWidget, BaseListHeaderWidget


class DeviceHeaderWidget(BaseListHeaderWidget):
    def __init__(self):
        super(DeviceHeaderWidget, self).__init__()

        self.layout.addWidget(
            self.property('Connected devices', alignment=Qt.AlignCenter)
        )


class DeviceListWidget(BaseListWidget):
    DEVICES_WORKER_ID = 200

    def __init__(self, parent):
        super(DeviceListWidget, self).__init__(parent)
        worker = AsyncRepositoryWorker(
            worker_id=self.DEVICES_WORKER_ID,
            name="Devices",
            repository_method=DeviceRepository.devices,
            arguments=(),
            response_callback=self.__async_response
        )
        if Adb.worker().work(worker):
            self.loading()
            worker.start()

    def __async_response(self, devices, error):
        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Devices',
                    timeout=15000,
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                )
            )

        widgets = []
        for device in devices:
            item = DeviceItemWidget(device)
            widgets.append(item)
        self.load(widgets, "There is no connected devices", False)


class DeviceItemWidget(BaseListItemWidget):
    def __init__(self, device: Device):
        super(DeviceItemWidget, self).__init__()
        self.device = device
        if device.type == DeviceType.DEVICE:
            self.layout.addWidget(self.icon(Resource.icon_phone))
        else:
            self.layout.addWidget(self.icon(Resource.icon_unknown))

        self.layout.addWidget(self.name(device.name))
        self.layout.addWidget(self.property(device.id))

    def mouseReleaseEvent(self, event):
        super(DeviceItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton and self.device.type == DeviceType.DEVICE:
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
