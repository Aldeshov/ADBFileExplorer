from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QStatusBar, QInputDialog, QMenuBar, QWidget, QLabel, \
    QApplication

from gui.abstract.base import BaseIconWidget
from gui.explorer.main import Explorer
from services.filesystem.config import Asset, VERSION
from services.models import Global
from services.shell import adb


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
        self.setFixedWidth(400)
        self.setFixedHeight(320)
        self.setWindowTitle('About')

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(int(center.x() - self.width() * 0.5), int(center.y() - self.height() * 0.5))


class StatusBar(QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()

    def message(self, st, msg):
        self.showMessage(st + " :  " + msg)


class MenuBar(QMenuBar):
    def __init__(self, statusbar):
        super(MenuBar, self).__init__()

        self.about = About()
        self.statusbar = statusbar
        self.file_menu = self.addMenu('&File')
        self.help_menu = self.addMenu('&Help')

        connect_action = QAction(QIcon(Asset.icon_connect), '&Connect', self)
        connect_action.setShortcut('Alt+C')
        connect_action.triggered.connect(self.connect_device)
        self.file_menu.addAction(connect_action)

        devices_action = QAction(QIcon(Asset.icon_phone), '&Show devices', self)
        devices_action.setShortcut('Alt+D')
        devices_action.triggered.connect(Global().communicate.devices.emit)
        self.file_menu.addAction(devices_action)

        exit_action = QAction(QIcon(Asset.icon_exit), '&Exit', self)
        exit_action.setShortcut('Alt+Q')
        exit_action.triggered.connect(qApp.quit)
        self.file_menu.addAction(exit_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.about.show)
        self.help_menu.addAction(about_action)

    def connect_device(self):
        self.statusbar.message('CONNECT', 'Connecting... Please wait')
        text, ok = QInputDialog.getText(self, 'New Device', 'Enter device ip:')
        self.statusbar.message('CONNECT', 'Canceled')

        if ok:
            message = adb.connect(str(text))
            self.statusbar.message('CONNECT', message)
            Global().communicate.devices.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setStatusBar(StatusBar())
        self.setMenuBar(MenuBar(self.statusBar()))
        self.setCentralWidget(Explorer(self.statusBar()))

        Global().communicate.devices.emit()

        self.move(300, 300)
        self.resize(640, 480)
        self.setMinimumWidth(480)
        self.setMinimumHeight(360)
        self.setWindowIcon(QIcon(Asset.logo))
        self.setWindowTitle('ADB File Explorer')

        self.statusBar().message('ADB', 'Ready')

    def closeEvent(self, event):
        # Stopping adb server
        # adb.kill_server()

        # close window
        event.accept()
