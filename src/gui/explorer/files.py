import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog
from typing import Optional

from core.configurations import Resource
from core.daemons import Adb
from core.managers import Global
from data.models import File, FileType, MessageData
from helpers.tools import AsyncRepositoryWorker
from data.repositories import FileRepository
from gui.abstract.base import BaseListItemWidget, BaseListWidget, BaseListHeaderWidget
from gui.others.notification import MessageType


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
        self.worker: Optional[AsyncRepositoryWorker] = None

    def update(self):
        super(FileListWidget, self).update()
        self.worker = AsyncRepositoryWorker(
            parent=self,
            worker_id=300,
            name="Disconnecting",
            repository_method=FileRepository.files,
            response_callback=self.__async_response,
            arguments=()
        )
        self.loading()
        self.worker.start()

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
            item = FileItemWidget(file, self.explorer)
            widgets.append(item)
        self.load(widgets, "Folder is empty")
        Global().communicate.path_toolbar__refresh.emit()

        # Important to add! close loading -> then kill worker
        self.worker.close()
        self.worker = None


class FileItemWidget(BaseListItemWidget):
    progress_callback = QtCore.pyqtSignal(str, int, int)

    def __init__(self, file: File, explorer):
        super(FileItemWidget, self).__init__()
        self.file = file
        self._written = 0
        self.explorer = explorer

        self.worker: Optional[AsyncRepositoryWorker] = None
        self.progress_callback.connect(self.update_progress)
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
                self.parent().update()

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

    def __async_response(self, data, error):
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
        self.worker.close()
        self.worker = None
        self._written = 0

    def download(self):
        if not self.worker:
            self.worker = AsyncRepositoryWorker(
                parent=self,
                worker_id=350,
                name="Download",
                repository_method=FileRepository.download,
                response_callback=self.__async_response,
                arguments=(self.progress_callback.emit, self.file.path)
            )
            Global().communicate.notification.emit(
                MessageData(
                    title="Downloading",
                    body="Downloading",
                    message_type=MessageType.LOADING_MESSAGE,
                    message_catcher=self.worker.set_loading_widget
                )
            )
            self.worker.loading_widget.setup_progress()
            self.worker.start()

    def update_progress(self, path, written, total):
        if self.worker and self.worker.loading_widget:
            self._written += int(written)
            self.worker.loading_widget.update_progress(f"SRC: {str(path)}", int((self._written / total * 100)))

    def download_to(self):
        if not self.worker:
            dir_name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
            if dir_name:
                self.worker = AsyncRepositoryWorker(
                    parent=self,
                    worker_id=375,
                    name="Download",
                    repository_method=FileRepository.download_to,
                    response_callback=self.__async_response,
                    arguments=(self.progress_callback.emit, self.file.path, dir_name)
                )
                Global().communicate.notification.emit(
                    MessageData(
                        title="Downloading to",
                        body="Downloading to",
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=self.worker.set_loading_widget
                    )
                )
                self.worker.loading_widget.setup_progress()
                self.worker.start()

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
