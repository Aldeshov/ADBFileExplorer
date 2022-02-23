from typing import Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QInputDialog, QMenuBar, QMessageBox

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from helpers.tools import AsyncRepositoryWorker
from data.repositories import DeviceRepository
from gui.explorer.main import Explorer
from gui.others.help import About
from gui.others.notification import NotificationCenter, MessageType
from data.models import MessageData


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super(MenuBar, self).__init__(parent)

        self.about = About()
        self.worker: Optional[AsyncRepositoryWorker] = None

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
        self.worker = AsyncRepositoryWorker(
            parent=self,
            worker_id=200,
            name="Disconnecting",
            repository_method=DeviceRepository.disconnect,
            response_callback=self.__async_response,
            arguments=()
        )
        Global().communicate.notification.emit(
            MessageData(
                title='Disconnecting',
                body="Disconnecting from devices, please wait",
                message_type=MessageType.LOADING_MESSAGE,
                height=80,
                message_catcher=self.worker.set_loading_widget
            )
        )
        Global().communicate.status_bar.emit(f'Operation: {self.worker.name}... Please wait.', 3000)
        self.worker.start()

    def connect_device(self):
        if not self.worker:
            text, ok = QInputDialog.getText(self, 'Connect Device', 'Enter device IP:')
            Global().communicate.status_bar.emit('Operation: Connecting canceled.', 3000)

            if ok and text:
                self.worker = AsyncRepositoryWorker(
                    parent=self,
                    worker_id=100,
                    name="Connecting to device",
                    repository_method=DeviceRepository.connect,
                    arguments=(str(text),),
                    response_callback=self.__async_response
                )
                Global().communicate.notification.emit(
                    MessageData(
                        title='Connecting',
                        body="Connecting to device via IP, please wait",
                        message_type=MessageType.LOADING_MESSAGE,
                        height=80,
                        message_catcher=self.worker.set_loading_widget
                    )
                )
                Global().communicate.status_bar.emit(f'Operation: {self.worker.name}... Please wait.', 3000)
                self.worker.start()

    def __async_response(self, data, error):
        if data:
            if self.worker.id == 100 and Adb.instance() == Adb.PYTHON_ADB:
                Global().communicate.files.emit()
            elif self.worker.id == 100:
                Global().communicate.devices.emit()
            elif self.worker.id == 200 and Adb.instance() == Adb.PYTHON_ADB:
                Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    title=self.worker.name,
                    body=data,
                    timeout=15000,
                    message_type=MessageType.MESSAGE,
                    height=100
                )
            )
        if error:
            Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    title=self.worker.name,
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    timeout=15000,
                    message_type=MessageType.MESSAGE,
                    height=100
                )
            )
        Global().communicate.status_bar.emit(f'Operation: {self.worker.name} finished.', 3000)

        # Important to add! close loading -> then kill worker
        self.worker.close()
        self.worker = None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setMenuBar(MenuBar(self))
        self.setCentralWidget(Explorer(self))

        self.move(300, 300)
        self.resize(640, 480)
        self.setMinimumWidth(480)
        self.setMinimumHeight(360)
        self.setWindowIcon(QIcon(Resource.logo))
        self.setWindowTitle('ADB File Explorer')

        # Show Devices Widget
        Global().communicate.devices.emit()

        # Connect to Global class to use it anywhere
        Global().communicate.status_bar.connect(self.statusBar().showMessage)

        # Important to add last to stay on top!
        self.notification_center = NotificationCenter(self)
        Global().communicate.notification.connect(self.notification_center.append_notification)

        # Welcome notification texts
        welcome_title = "Welcome to ADBFileExplorer!"
        welcome_body = "Here you can see the list of your connected adb devices. Click one of them to see files." \
                       " Also you can connect to devices via TCP in the File tab -> Connect -> then enter Device IP." \
                       " Good Luck!"

        Global().communicate.status_bar.emit('Ready', 5000)
        Global().communicate.notification.emit(
            MessageData(
                title=welcome_title,
                body=welcome_body,
                timeout=30000,
                message_type=MessageType.MESSAGE
            )
        )

    def closeEvent(self, event):
        if Adb.instance() == Adb.COMMON_ANDROID_ADB:
            reply = QMessageBox.question(self, 'ADB Server', "Do you want to kill adb server?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                Adb.stop()
        elif Adb.instance() == Adb.PYTHON_ADB:
            Adb.stop()

        event.accept()

    # This helps the toast maintain the place after window get resized
    def resizeEvent(self, e):
        if self.notification_center:
            self.notification_center.update_position()
        return super().resizeEvent(e)
