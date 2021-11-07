from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QInputDialog, QMenuBar, QMessageBox

from gui.explorer.main import Explorer
from gui.others.help import About
from services.filesystem.config import Asset
from services.models import Global
from services.shell import adb


class MenuBar(QMenuBar):
    def __init__(self, mainwindow: QMainWindow):
        super(MenuBar, self).__init__()

        self.about = About()
        self.mainwindow = mainwindow
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
        self.mainwindow.statusBar().showMessage('Connecting... Please wait')
        text, ok = QInputDialog.getText(self, 'New Device', 'Enter device ip:')
        self.mainwindow.statusBar().showMessage('Connecting canceled.', 3000)

        if ok:
            message = adb.connect(str(text))
            QMessageBox.information(self.mainwindow, 'Connect', message)
            Global().communicate.devices.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setCentralWidget(Explorer(self))
        self.setMenuBar(MenuBar(self))

        Global().communicate.devices.emit()

        self.move(300, 300)
        self.resize(640, 480)
        self.setMinimumWidth(480)
        self.setMinimumHeight(360)
        self.setWindowIcon(QIcon(Asset.logo))
        self.setWindowTitle('ADB File Explorer')

        self.statusBar().showMessage('Ready', 5)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'ADB Server', "Do you want to kill adb server?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            adb.kill_server()
        event.accept()
