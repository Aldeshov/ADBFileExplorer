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
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QApplication

from core.configurations import Resources, Application


class About(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        icon = QLabel(self)
        icon.setPixmap(QPixmap(Resources.icon_logo).scaled(64, 64, Qt.KeepAspectRatio))
        icon.move(168, 40)
        about_text = "<br/><br/>"
        about_text += "<b>ADB File Explorer</b><br/>"
        about_text += f"<i>Version: {Application.__version__}</i><br/>"
        about_text += '<br/>'
        about_text += "Open source application written in <i>Python</i><br/>"
        about_text += "UI Library: <i>PyQt5</i><br/>"
        about_text += "Developer: Azat Aldeshov<br/>"
        link = 'https://github.com/Aldeshov/ADBFileExplorer'
        about_text += f"Github: <a target='_blank' href='{link}'>{link}</a>"
        about_label = QLabel(about_text, self)
        about_label.setOpenExternalLinks(True)
        about_label.move(10, 100)

        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowIcon(QIcon(Resources.icon_logo))
        self.setWindowTitle('About')
        self.setFixedHeight(320)
        self.setFixedWidth(400)

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(int(center.x() - self.width() * 0.5), int(center.y() - self.height() * 0.5))