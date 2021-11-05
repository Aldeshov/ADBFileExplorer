from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QStatusBar, QInputDialog, QMenuBar

from gui.explorer.main import Explorer
from services.filesystem.config import Asset
from services.manager import FileManager
from services.models import Single
from services.shell import adb


class StatusBar(QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()

    def message(self, st, msg):
        self.showMessage(st + " :  " + msg)


class MenuBar(QMenuBar):
    def __init__(self, statusbar):
        super(MenuBar, self).__init__()
        self.statusbar = statusbar

        connect_action = QAction(QIcon(Asset.icon_connect), '&Connect', self)
        connect_action.setShortcut('Alt+C')
        connect_action.triggered.connect(self.connect_device)

        devices_action = QAction(QIcon(Asset.icon_phone), '&Show devices', self)
        devices_action.setShortcut('Alt+D')
        devices_action.triggered.connect(self.show_devices)

        exit_action = QAction(QIcon(Asset.icon_exit), '&Exit', self)
        exit_action.setShortcut('Alt+Q')
        exit_action.triggered.connect(qApp.quit)

        file_menu = self.addMenu('&File')
        file_menu.addAction(connect_action)
        file_menu.addAction(devices_action)
        file_menu.addAction(exit_action)

    def connect_device(self):
        self.statusbar.message('CONNECT', 'Connecting... Please wait')
        text, ok = QInputDialog.getText(self, 'New Device', 'Enter device ip:')
        self.statusbar.message('CONNECT', 'Canceled')

        if ok:
            message = adb.connect(str(text))
            self.statusbar.message('CONNECT', message)
            Single().communicate.devices.emit()
            FileManager.clear_device()

    @staticmethod
    def show_devices():
        Single().communicate.devices.emit()
        FileManager.clear_device()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStatusBar(StatusBar())
        self.setMenuBar(MenuBar(self.statusBar()))
        self.setCentralWidget(Explorer(self.statusBar()))

        Single().communicate.devices.emit()

        self.move(300, 300)
        self.resize(640, 480)
        self.setMinimumWidth(480)
        self.setMinimumHeight(360)
        self.setWindowIcon(QIcon(Asset.logo))
        self.setWindowTitle('ADB File Explorer')

        self.statusBar().message('ADB', 'Ready')

    def closeEvent(self, event):
        # adb.kill_server()

        # close window
        event.accept()
