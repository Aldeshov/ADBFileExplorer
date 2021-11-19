from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QInputDialog, QMenuBar, QMessageBox

from gui.explorer.main import Explorer
from gui.others.help import About
from config import Resource
from services.data.managers import Global
from services.data.repositories import DeviceRepository
from services.shell import adb


class MenuBar(QMenuBar):
    def __init__(self, main_window: QMainWindow):
        super(MenuBar, self).__init__()

        self.about = About()
        self.main_window = main_window
        self.file_menu = self.addMenu('&File')
        self.help_menu = self.addMenu('&Help')

        connect_action = QAction(QIcon(Resource.icon_connect), '&Connect', self)
        connect_action.setShortcut('Alt+C')
        connect_action.triggered.connect(self.connect_device)
        self.file_menu.addAction(connect_action)

        disconnect_action = QAction(QIcon(Resource.icon_disconnect), '&Disconnect', self)
        disconnect_action.setShortcut('Alt+X')
        disconnect_action.triggered.connect(self.disconnect)
        self.file_menu.addAction(disconnect_action)

        devices_action = QAction(QIcon(Resource.icon_phone), '&Show devices', self)
        devices_action.setShortcut('Alt+D')
        devices_action.triggered.connect(Global().communicate.devices.emit)
        self.file_menu.addAction(devices_action)

        exit_action = QAction(QIcon(Resource.icon_exit), '&Exit', self)
        exit_action.setShortcut('Alt+Q')
        exit_action.triggered.connect(qApp.quit)
        self.file_menu.addAction(exit_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.about.show)
        self.help_menu.addAction(about_action)

    def disconnect(self):
        data, error = DeviceRepository.disconnect()
        if data:
            QMessageBox.information(self.main_window, 'Disconnect', data)
        if error:
            QMessageBox.critical(self.main_window, 'Disconnect', error)
        Global().communicate.devices.emit()

    def connect_device(self):
        self.main_window.statusBar().showMessage('Connecting... Please wait')
        text, ok = QInputDialog.getText(self, 'New Device', 'Enter device ip:')
        self.main_window.statusBar().showMessage('Connecting canceled.', 3000)

        if ok:
            data, error = DeviceRepository.connect(str(text))
            if data:
                QMessageBox.information(self.main_window, 'Connect', data)
            if error:
                QMessageBox.critical(self.main_window, 'Connect', error)
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
        self.setWindowIcon(QIcon(Resource.logo))
        self.setWindowTitle('ADB File Explorer')

        self.statusBar().showMessage('Ready', 5)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'ADB Server', "Do you want to kill adb server?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            adb.kill_server()
            print("ADB server stopped")
        event.accept()
