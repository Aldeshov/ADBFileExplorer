from PyQt5.QtCore import Qt

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import Device, DeviceType, MessageData
from helpers.tools import AsyncRepositoryWorker
from data.repositories import DeviceRepository
from gui.abstract.base import BaseListWidget, BaseListItemWidget, BaseListHeaderWidget
from gui.others.notification import MessageType


class DeviceHeaderWidget(BaseListHeaderWidget):
    def __init__(self):
        super(DeviceHeaderWidget, self).__init__()

        self.layout.addWidget(
            self.property('Connected devices', alignment=Qt.AlignCenter)
        )


class DeviceListWidget(BaseListWidget):
    def __init__(self):
        super(DeviceListWidget, self).__init__()
        self.worker = AsyncRepositoryWorker(
            parent=self,
            worker_id=100,
            name="Devices",
            repository_method=DeviceRepository.devices,
            arguments=(),
            response_callback=self.__async_response
        )
        self.loading()
        self.worker.start()

    def __async_response(self, devices, error):
        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Devices',
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    timeout=15000,
                    message_type=MessageType.MESSAGE,
                    height=120
                )
            )

        widgets = []
        for device in devices:
            item = DeviceItemWidget(device)
            widgets.append(item)
        self.load(widgets, "There is no connected devices", False)

        # Important to add! close loading -> then kill worker
        self.worker.close()
        self.worker = None


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
                        body=f"Could not open the device {Adb.manager().get_device().name}",
                        message_type=MessageType.MESSAGE,
                        height=80
                    )
                )
