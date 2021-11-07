import threading
import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QWidget, QLabel, QVBoxLayout, QDialog, QPushButton, QFileDialog

from gui.abstract.base import BaseListItemWidget, BaseListWidget, BaseListHeaderWidget
from services.drivers import get_files, download_files, download_files_to
from services.filesystem.config import Asset
from services.manager import FileManager
from services.models import File, FileTypes, Global


class FileHeaderWidget(BaseListHeaderWidget):
    def __init__(self):
        super(FileHeaderWidget, self).__init__()

        self.layout.addWidget(
            BaseListItemWidget.name('File', margin=48)
        )

        self.layout.addWidget(
            self.property('Permissions', alignment=Qt.AlignCenter)
        )

        self.layout.addWidget(
            self.property('Size', alignment=Qt.AlignCenter)
        )

        self.layout.addWidget(
            self.property('Date', alignment=Qt.AlignCenter, stretch=3)
        )


class FileListWidget(BaseListWidget):
    def __init__(self, explorer):
        super(FileListWidget, self).__init__()
        self.explorer = explorer
        self.files_widgets()

    def update(self):
        super(FileListWidget, self).update()
        self.files_widgets()

    def files_widgets(self):
        files = get_files(FileManager.get_device(), FileManager.path())
        widgets = []
        for file in files:
            item = FileItemWidget(file, self.explorer)
            widgets.append(item)
        self.load(widgets, "Folder is empty")


class FileItemWidget(BaseListItemWidget):
    def __init__(self, file: File, explorer):
        super(FileItemWidget, self).__init__()
        self.file = file
        self.explorer = explorer
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        self.layout.addWidget(
            self.icon(self.icon_path)
        )

        self.layout.addWidget(
            self.name(self.file.name)
        )

        self.layout.addWidget(self.separator())

        self.layout.addWidget(
            self.property(self.file.permissions, font_style="italic", alignment=Qt.AlignCenter)
        )

        self.layout.addWidget(self.separator())

        self.layout.addWidget(
            self.property(self.file.size, alignment=Qt.AlignCenter)
        )

        self.layout.addWidget(self.separator())

        self.layout.addWidget(
            self.property(self.file.date, alignment=Qt.AlignCenter, stretch=3)
        )

        self.setToolTip(self.file.name)
        if self.file.type == FileTypes.LINK:
            self.setToolTip(self.file.link)

    @property
    def icon_path(self):
        if self.file.type == FileTypes.DIRECTORY:
            return Asset.icon_folder
        elif self.file.type == FileTypes.FILE:
            return Asset.icon_file
        elif self.file.type == FileTypes.LINK:
            return Asset.icon_link_file_universal
            # if self.file.link_type == FileTypes.DIRECTORY:
            #     return Asset.icon_link_folder
            # elif self.file.link_type == FileTypes.FILE:
            #     return Asset.icon_link_file
            # return Asset.icon_link_file_unknown
        return Asset.icon_file_unknown

    def mouseReleaseEvent(self, event):
        super(FileItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            if FileManager.open(self.file):
                self.parent().update()

    def context_menu(self, pos: QPoint):
        global_pos = self.mapToGlobal(pos)

        action_properties = QAction('Properties', self)
        action_properties.triggered.connect(self.file_properties)

        action_copy = QAction('Copy to...', self)
        action_move = QAction('Move to...', self)
        action_delete = QAction('Delete', self)
        action_rename = QAction('Rename', self)

        action_download = QAction('Download', self)
        action_download.triggered.connect(self.download)

        action_download_to = QAction('Download to...', self)
        action_download_to.triggered.connect(self.download_to)

        menu = QMenu()
        menu.addSection("Actions")
        menu.addAction(action_copy)
        menu.addAction(action_move)
        menu.addAction(action_delete)
        menu.addAction(action_rename)
        menu.addAction(action_download)
        menu.addAction(action_download_to)
        menu.addSeparator()
        menu.addAction(action_properties)

        menu.exec(global_pos)

    def download(self):
        message = download_files(devices_id=FileManager.get_device(), source=self.file.path)
        QMessageBox.information(self, 'Download', message)
        self.explorer.mainwindow.statusBar().showMessage('Done', 3000)

    def download_to(self):
        name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
        self.explorer.mainwindow.statusBar().showMessage('Canceled.', 3000)
        if name:
            message = download_files_to(devices_id=FileManager.get_device(), source=self.file.path, destination=name)
            QMessageBox.information(self, 'Download', message)
            self.explorer.mainwindow.statusBar().showMessage('Done', 3000)

    def file_properties(self):
        info = f"<br/><u><b>{str(self.file)}</b></u><br/>"
        info += f"<pre>Name:        {self.file.name or '-'}</pre>"
        info += f"<pre>Owner:       {self.file.owner or '-'}</pre>"
        info += f"<pre>Group:       {self.file.group or '-'}</pre>"
        info += f"<pre>Size:        {self.file.size or '-'}</pre>"
        info += f"<pre>Permissions: {self.file.permissions or '-'}</pre>"
        info += f"<pre>Date:        {self.file.date_raw or '-'}</pre>"
        info += f"<pre>Type:        {self.file.type or '-'}</pre>"

        if self.file.type == FileTypes.LINK:
            info += f"<pre>Links to:    {self.file.link or '-'}</pre>"

        QMessageBox.information(self, 'Properties', info)
