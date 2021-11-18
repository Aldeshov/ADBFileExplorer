from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from gui.abstract.base import BaseListWidget, BaseListItemWidget, BaseListHeaderWidget
from config import Resource
from services.data.managers import FileManager, Global
from services.data.models import Device, DeviceType
from services.data.repositories import DeviceRepository


class DeviceHeaderWidget(BaseListHeaderWidget):
    def __init__(self):
        super(DeviceHeaderWidget, self).__init__()

        self.layout.addWidget(
            self.property('Connected devices', alignment=Qt.AlignCenter)
        )


class DeviceListWidget(BaseListWidget):
    def __init__(self):
        super(DeviceListWidget, self).__init__()
        devices, error = DeviceRepository.devices()
        if error:
            QMessageBox.critical(self, 'Devices', error)

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
        self.layout.addWidget(self.property(device.id,))

    def mouseReleaseEvent(self, event):
        super(DeviceItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton and self.device.type == DeviceType.DEVICE:
            FileManager.set_device(self.device.id)
            Global().communicate.files.emit()
