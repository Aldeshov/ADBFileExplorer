# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QInputDialog, QMenuBar, QMessageBox

from app.core.configurations import Resources, Settings
from app.core.main import Adb
from app.core.managers import Global
from app.data.models import MessageData, MessageType
from app.data.repositories import DeviceRepository
from app.gui.explorer import MainExplorer
from app.gui.help import About
from app.gui.notification import NotificationCenter
from app.helpers.tools import AsyncRepositoryWorker


class MenuBar(QMenuBar):
    CONNECT_WORKER_ID = 100
    DISCONNECT_WORKER_ID = 101

    def __init__(self, parent):
        super(MenuBar, self).__init__(parent)

        self.about = About()
        self.file_menu = self.addMenu('&File')
        self.help_menu = self.addMenu('&Help')

        self.connect_action = QAction(QIcon(Resources.icon_link), '&Connect', self)
        self.connect_action.setShortcut('Alt+C')
        self.connect_action.triggered.connect(self.connect_device)
        self.file_menu.addAction(self.connect_action)

        disconnect_action = QAction(QIcon(Resources.icon_no_link), '&Disconnect', self)
        disconnect_action.setShortcut('Alt+X')
        disconnect_action.triggered.connect(self.disconnect)
        self.file_menu.addAction(disconnect_action)

        devices_action = QAction(QIcon(Resources.icon_phone), '&Show devices', self)
        devices_action.setShortcut('Alt+D')
        devices_action.triggered.connect(Global().communicate.devices.emit)
        self.file_menu.addAction(devices_action)

        exit_action = QAction('&Exit', self)
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
            Global().communicate.status_bar.emit('Operation: %s... Please wait.', 3000) % worker.name
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
                Global().communicate.status_bar.emit('Operation: %s... Please wait.', 3000) % worker.name
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
                    body="<span style='color: red; font-weight: 600'></span>" % error
                )
            )
        Global().communicate.status_bar.emit('Operation: Disconnecting finished.', 3000)

    @staticmethod
    def __async_response_connect(data, error):
        if data:
            if Adb.core == Adb.PYTHON_ADB_SHELL:
                Global().communicate.files.emit()
            elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
                Global().communicate.devices.emit()
            Global().communicate.notification.emit(MessageData(title="Connecting to device", timeout=15000, body=data))
        if error:
            Global().communicate.devices.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=15000,
                    title="Connect to device",
                    body="<span style='color: red; font-weight: 600'>%s</span>" % error
                )
            )
        Global().communicate.status_bar.emit('Operation: Connecting to device finished.', 3000)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setMenuBar(MenuBar(self))
        self.setCentralWidget(MainExplorer(self))

        self.resize(640, 480)
        self.setMinimumSize(480, 360)
        self.setWindowTitle('ADB File Explorer')
        self.setWindowIcon(QIcon(Resources.icon_logo))

        # Show Devices Widget
        Global().communicate.devices.emit()

        # Connect to Global class to use it anywhere
        Global().communicate.status_bar.connect(self.statusBar().showMessage)

        # Important to add last to stay on top!
        self.notification_center = NotificationCenter(self)
        Global().communicate.notification.connect(self.notify)

        # Welcome notification texts
        welcome_title = "Welcome to ADBFileExplorer!"
        welcome_body = "Here you can see the list of your connected adb devices. Click one of them to see files.<br/>"\
                       "Current selected core: <strong>%s</strong><br/>" \
                       "To change it - <code style='color: blue'>settings.json</code> file" % Settings.adb_core()

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
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            if Settings.adb_kill_server_at_exit() is None:
                reply = QMessageBox.question(self, 'ADB Server', "Do you want to kill adb server?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    Adb.stop()
            elif Settings.adb_kill_server_at_exit():
                Adb.stop()
        elif Adb.core == Adb.PYTHON_ADB_SHELL:
            Adb.stop()

        event.accept()

    # This helps the "notification_center" maintain the place after window get resized
    def resizeEvent(self, e):
        if self.notification_center:
            self.notification_center.update_position()
        return super(MainWindow, self).resizeEvent(e)
