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

import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import File, FileType, MessageData, MessageType
from data.repositories import FileRepository
from gui.abstract.base import BaseListItemWidget, BaseListWidget, BaseListHeaderWidget
from helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper


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
    FILES_WORKER_ID = 300

    def __init__(self, parent):
        super(FileListWidget, self).__init__(parent)

    def update(self):
        super(FileListWidget, self).update()
        worker = AsyncRepositoryWorker(
            worker_id=self.FILES_WORKER_ID,
            name="Files",
            repository_method=FileRepository.files,
            response_callback=self.__async_response,
            arguments=()
        )
        if Adb.worker().work(worker):
            self.loading()
            worker.start()

    def __async_response(self, files, error):
        if error:
            print(error, file=sys.stderr)
        if error and not files:
            Global().communicate.notification.emit(
                MessageData(
                    title='Files',
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    timeout=15000,
                    message_type=MessageType.MESSAGE,
                    height=100
                )
            )

        widgets = []
        for file in files:
            item = FileItemWidget(self, file)
            widgets.append(item)
        self.load(widgets, "Folder is empty")
        Global().communicate.path_toolbar__refresh.emit()


class FileItemWidget(BaseListItemWidget):
    DOWNLOAD_WORKER_ID = 399

    def __init__(self, parent, file: File):
        super(FileItemWidget, self).__init__(parent)
        self.file = file

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
        if self.file.type == FileType.LINK:
            self.setToolTip(self.file.link)

    @property
    def icon_path(self):
        if self.file.type == FileType.DIRECTORY:
            return Resource.icon_folder
        elif self.file.type == FileType.FILE:
            return Resource.icon_file
        elif self.file.type == FileType.LINK:
            if self.file.link_type == FileType.DIRECTORY:
                return Resource.icon_link_folder
            elif self.file.link_type == FileType.FILE:
                return Resource.icon_link_file
            return Resource.icon_link_file_unknown
        return Resource.icon_file_unknown

    def mouseReleaseEvent(self, event):
        super(FileItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            if Adb.manager().open(self.file):
                Global().communicate.files__refresh.emit()

    def context_menu(self, pos: QPoint):
        menu = QMenu()
        menu.addSection("Actions")

        action_copy = QAction('Copy to...', self)
        action_copy.setDisabled(True)
        menu.addAction(action_copy)

        action_move = QAction('Move to...', self)
        action_move.setDisabled(True)
        menu.addAction(action_move)

        action_rename = QAction('Rename', self)
        action_rename.setDisabled(True)
        menu.addAction(action_rename)

        action_delete = QAction('Delete', self)
        action_delete.setDisabled(True)
        menu.addAction(action_delete)

        action_download = QAction('Download', self)
        action_download.triggered.connect(self.download)
        menu.addAction(action_download)

        action_download_to = QAction('Download to...', self)
        action_download_to.triggered.connect(self.download_to)
        menu.addAction(action_download_to)

        menu.addSeparator()

        action_properties = QAction('Properties', self)
        action_properties.triggered.connect(self.file_properties)
        menu.addAction(action_properties)

        menu.exec(self.mapToGlobal(pos))

    @staticmethod
    def __async_response(data, error):
        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Download error',
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    timeout=15000,
                    message_type=MessageType.MESSAGE,
                    height=100
                )
            )
        if data:
            Global().communicate.notification.emit(
                MessageData(
                    title='Downloaded',
                    body=data,
                    timeout=15000,
                    message_type=MessageType.MESSAGE
                )
            )

    def download(self):
        helper = ProgressCallbackHelper()
        worker = AsyncRepositoryWorker(
            worker_id=self.DOWNLOAD_WORKER_ID,
            name="Download",
            repository_method=FileRepository.download,
            response_callback=FileItemWidget.__async_response,
            arguments=(helper.progress_callback.emit, self.file.path)
        )
        if Adb.worker().work(worker):
            Global().communicate.notification.emit(
                MessageData(
                    title="Downloading",
                    body="Downloading",
                    message_type=MessageType.LOADING_MESSAGE,
                    message_catcher=worker.set_loading_widget
                )
            )
            helper.setup(worker, worker.update_loading_widget)
            worker.loading_widget.setup_progress()
            worker.start()

    def download_to(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
        if dir_name:
            helper = ProgressCallbackHelper()
            worker = AsyncRepositoryWorker(
                worker_id=self.DOWNLOAD_WORKER_ID,
                name="Download",
                repository_method=FileRepository.download_to,
                response_callback=FileItemWidget.__async_response,
                arguments=(helper.progress_callback.emit, self.file.path, dir_name)
            )
            if Adb.worker().work(worker):
                Global().communicate.notification.emit(
                    MessageData(
                        title="Downloading to",
                        body="Downloading to",
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=worker.set_loading_widget
                    )
                )
                helper.setup(worker, worker.update_loading_widget)
                worker.loading_widget.setup_progress()
                worker.start()

    def file_properties(self):
        info = f"<br/><u><b>{str(self.file)}</b></u><br/>"
        info += f"<pre>Name:        {self.file.name or '-'}</pre>"
        info += f"<pre>Owner:       {self.file.owner or '-'}</pre>"
        info += f"<pre>Group:       {self.file.group or '-'}</pre>"
        info += f"<pre>Size:        {self.file.size or '-'}</pre>"
        info += f"<pre>Permissions: {self.file.permissions or '-'}</pre>"
        info += f"<pre>Date:        {self.file.date__raw or '-'}</pre>"
        info += f"<pre>Type:        {self.file.type or '-'}</pre>"

        if self.file.type == FileType.LINK:
            info += f"<pre>Links to:    {self.file.link or '-'}</pre>"

        QMessageBox.information(self, 'Properties', info)
