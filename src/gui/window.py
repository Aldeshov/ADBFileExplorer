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

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QInputDialog, QMenuBar, QMessageBox

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import MessageData, MessageType
from data.repositories import DeviceRepository
from gui.explorer.main import Explorer
from gui.others.help import About
from gui.others.notification import NotificationCenter
from helpers.tools import AsyncRepositoryWorker


class MenuBar(QMenuBar):
    CONNECT_WORKER_ID = 100
    DISCONNECT_WORKER_ID = 101

    def __init__(self, parent):
        super(MenuBar, self).__init__(parent)

        self.about = About()
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
        worker = AsyncRepositoryWorker(
            worker_id=self.DISCONNECT_WORKER_ID,
            name="Disconnecting",
            repository_method=DeviceRepository.disconnect,
            response_callback=self.__async_response_disconnect,
            arguments=()
        )
        if Adb.worker().work(worker):
            Global().communicate.notification.emit(
                MessageData(
                    title='Disconnect',
                    body="Disconnecting from devices, please wait",
                    message_type=MessageType.LOADING_MESSAGE,
                    message_catcher=worker.set_loading_widget
                )
            )
            Global().communicate.status_bar.emit(f'Operation: {worker.name}... Please wait.', 3000)
            worker.start()

    def connect_device(self):
        text, ok = QInputDialog.getText(self, 'Connect Device', 'Enter device IP:')
        Global().communicate.status_bar.emit('Operation: Connecting canceled.', 3000)

        if ok and text:
            worker = AsyncRepositoryWorker(
                worker_id=self.CONNECT_WORKER_ID,
                name="Connecting to device",
                repository_method=DeviceRepository.connect,
                arguments=(str(text),),
                response_callback=self.__async_response_connect
            )
            if Adb.worker().work(worker):
                Global().communicate.notification.emit(
                    MessageData(
                        title='Connect',
                        body="Connecting to device via IP, please wait",
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=worker.set_loading_widget
                    )
                )
                Global().communicate.status_bar.emit(f'Operation: {worker.name}... Please wait.', 3000)
                worker.start()

    @staticmethod
    def __async_response_disconnect(data, error):
        if data:
            Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    title="Disconnect",
                    timeout=15000,
                    body=data
                )
            )
        if error:
            Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=15000,
                    title="Disconnect",
                    body=f"<span style='color: red; font-weight: 600'>{error}</span>"
                )
            )
        Global().communicate.status_bar.emit('Operation: Disconnecting finished.', 3000)

    @staticmethod
    def __async_response_connect(data, error):
        if data:
            if Adb.CORE == Adb.PYTHON_ADB:
                Global().communicate.files.emit()
            elif Adb.CORE == Adb.COMMON_ANDROID_ADB:
                Global().communicate.devices.emit()
            Global().communicate.notification.emit(MessageData(title="Connecting to device", timeout=15000, body=data))
        if error:
            Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=15000,
                    title="Connect to device",
                    body=f"<span style='color: red; font-weight: 600'>{error}</span>"
                )
            )
        Global().communicate.status_bar.emit('Operation: Connecting to device finished.', 3000)


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
        Global().communicate.notification.connect(self.notify)

        # Welcome notification texts
        welcome_title = "Welcome to ADBFileExplorer!"
        welcome_body = "Here you can see the list of your connected adb devices. Click one of them to see files." \
                       " Also you can connect to devices via TCP in the File tab -> Connect -> then enter Device IP." \
                       " Good Luck!"

        Global().communicate.status_bar.emit('Ready', 5000)
        Global().communicate.notification.emit(MessageData(title=welcome_title, body=welcome_body, timeout=30000))

    def notify(self, data: MessageData):
        message = self.notification_center.append_notification(
            title=data.title,
            body=data.body,
            timeout=data.timeout,
            message_type=data.message_type
        )
        if data.message_catcher:
            data.message_catcher(message)

    def closeEvent(self, event):
        if Adb.CORE == Adb.COMMON_ANDROID_ADB:
            reply = QMessageBox.question(self, 'ADB Server', "Do you want to kill adb server?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                Adb.stop()
        elif Adb.CORE == Adb.PYTHON_ADB:
            Adb.stop()

        event.accept()

    # This helps the toast maintain the place after window get resized
    def resizeEvent(self, e):
        if self.notification_center:
            self.notification_center.update_position()
        return super().resizeEvent(e)
