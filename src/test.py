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

# from adb_shell.adb_device import AdbDeviceUsb
#
# from helpers.tools import get_python_rsa_keys_signer
#
# device = AdbDeviceUsb()
# device.connect(rsa_keys=[get_python_rsa_keys_signer()], auth_timeout_s=0.1)
#
#
# if __name__ == "__main__":
#     files = device.list('/sdcard/Download/')
#     for file in files:
#         print(file)
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

from data.models import MessageType
from gui.others.additional import LoadingWidget
from gui.others.notification import NotificationCenter


class NotifyExample(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.setLayout(QGridLayout(self))

        button_notify = QPushButton('Notify', self)
        button_notify.clicked.connect(self.notify)
        self.layout().addWidget(button_notify)

        button_loading = QPushButton('Loading', self)
        button_loading.clicked.connect(self.old_loading)
        self.layout().addWidget(button_loading)

        self.setMinimumSize(640, 480)
        self.notification_center = NotificationCenter(self)
        self.notification_center.setStyleSheet("background: #00FF00")  # Scroll Area Test

    def notify(self):
        if self.counter % 2 == 0:
            text = "Lorem ipsum dolor sit amet, consecrate disciplining elit," \
                   "sed do usermod tempor incident ut labor et color magna aliquot." \
                   "Ut enum ad minim venial, quits nostrum excitation McCull-och labors" \
                   "nisei ut aliquot ex ea common consequent. Dis auto inure dolor in" \
                   "reprehend in voluptuary valid esse cilium color eu fugit null" \
                   "paginator. Except saint toccata cupidity non president, sunt in gulp" \
                   "qui official underused moll-it anim id est labor."
            self.notification_center.append_notification(title="Message TEST", body=text, timeout=10000)
        elif self.counter % 2 == 1:
            self.notification_center.append_notification(
                title="Message",
                body=f"<span style='color: red; font-weight: 600'>Lorem ipsum dolor sit amet</span>",
                message_type=MessageType.LOADING_MESSAGE
            )
        self.counter = self.counter + 1

    def old_loading(self):
        LoadingWidget(self, "Loading, please wait... (ALT+F4 to stop)")

    def resizeEvent(self, e):
        if self.notification_center:
            self.notification_center.update_position()
        return super().resizeEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    toastExample = NotifyExample()
    toastExample.show()
    app.exec_()
