from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QApplication

from gui.abstract.base import BaseIconWidget
from services.filesystem.config import Asset, VERSION


class About(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        icon = BaseIconWidget(Asset.logo, width=64, height=64, context=self)
        icon.move(168, 40)
        about_text = "<br/><br/>"
        about_text += "<b>ADB File Explorer</b><br/>"
        about_text += f"<i>Version: {VERSION}</i><br/>"
        about_text += '<br/>'
        about_text += "Open source application written in <i>Python</i><br/>"
        about_text += "UI Library: <i>PyQt5</i><br/>"
        about_text += "Developer: Azat<br/>"
        link = 'https://github.com/Aldeshov/ADBFileExplorer'
        about_text += f"Github: <a target='_blank' href='{link}'>{link}</a>"
        about_label = QLabel(about_text, self)
        about_label.setOpenExternalLinks(True)
        about_label.move(10, 100)

        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowIcon(QIcon(Asset.logo))
        self.setWindowTitle('About')
        self.setFixedHeight(320)
        self.setFixedWidth(400)

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(int(center.x() - self.width() * 0.5), int(center.y() - self.height() * 0.5))