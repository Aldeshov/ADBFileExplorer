from PyQt5.QtCore import Qt

from gui.abstract.base import BaseListWidget, BaseListItemWidget, BaseListHeaderWidget
from services.drivers import get_devices
from services.filesystem.config import Asset
from services.manager import FileManager
from services.models import Device, Global


class DeviceHeaderWidget(BaseListHeaderWidget):
    def __init__(self):
        super(DeviceHeaderWidget, self).__init__()

        self.layout.addWidget(
            self.property('Connected devices', alignment=Qt.AlignCenter)
        )


class DeviceListWidget(BaseListWidget):
    def __init__(self):
        super().__init__()
        self.devices_widgets()

    def devices_widgets(self):
        devices = get_devices()
        if not devices:
            self.empty("There is no connected devices", False)
        else:
            widgets = []
            for device in devices:
                item = DeviceItemWidget(device)
                widgets.append(item)
            self.load(widgets)


class DeviceItemWidget(BaseListItemWidget):
    def __init__(self, device: Device):
        super().__init__()
        self.device = device
        if device.type == 'device':
            self.layout.addWidget(self.icon(Asset.icon_phone))
        else:
            self.layout.addWidget(self.icon(Asset.icon_unknown))

        self.layout.addWidget(self.name(device.name))
        self.layout.addWidget(self.property(device.id,))

    def mouseReleaseEvent(self, event):
        super(DeviceItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton and self.device.type == 'device':
            FileManager.set_device(self.device.id)
            Global().communicate.files.emit()
