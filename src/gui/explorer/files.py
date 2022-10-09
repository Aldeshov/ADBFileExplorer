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

from genericpath import isdir
import sys
from typing import List, Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QModelIndex, QAbstractListModel, QVariant, QRect, QSize, QEvent, QObject
from PyQt5.QtGui import QPixmap, QColor, QPalette, QMovie, QKeySequence
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog, QStyle, QWidget, QStyledItemDelegate, \
    QStyleOptionViewItem, QApplication, QListView, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QTextEdit, \
    QMainWindow

from core.configurations import Resources
from core.main import Adb
from core.managers import Global
from data.models import File, FileType, MessageData, MessageType
from data.repositories import FileRepository
from gui.explorer.toolbar import ParentButton, UploadTools, PathBar
from helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper, read_string_from_file


class FileHeaderWidget(QWidget):
    def __init__(self, parent=None):
        super(FileHeaderWidget, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        self.file = QLabel('File', self)
        self.file.setContentsMargins(45, 0, 0, 0)
        policy.setHorizontalStretch(39)
        self.file.setSizePolicy(policy)
        self.layout().addWidget(self.file)

        self.permissions = QLabel('Permissions', self)
        self.permissions.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(18)
        self.permissions.setSizePolicy(policy)
        self.layout().addWidget(self.permissions)

        self.size = QLabel('Size', self)
        self.size.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(21)
        self.size.setSizePolicy(policy)
        self.layout().addWidget(self.size)

        self.date = QLabel('Date', self)
        self.date.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(22)
        self.date.setSizePolicy(policy)
        self.layout().addWidget(self.date)

        self.setStyleSheet("QWidget { background-color: #E5E5E5; font-weight: 500; border: 1px solid #C0C0C0 }")


class FileExplorerToolbar(QWidget):
    def __init__(self, parent=None):
        super(FileExplorerToolbar, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)

        self.upload_tools = UploadTools(self)
        self.upload_tools.setSizePolicy(policy)
        self.layout().addWidget(self.upload_tools)

        self.parent_button = ParentButton(self)
        self.parent_button.setSizePolicy(policy)
        self.layout().addWidget(self.parent_button)

        self.path_bar = PathBar(self)
        policy.setHorizontalStretch(8)
        self.path_bar.setSizePolicy(policy)
        self.layout().addWidget(self.path_bar)


class FileItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        result = super(FileItemDelegate, self).sizeHint(option, index)
        result.setHeight(40)
        return result

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex):
        editor.setText(index.model().data(index, Qt.EditRole))

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        editor.setGeometry(
            option.rect.left() + 48, option.rect.top(), int(option.rect.width() / 2.5) - 55, option.rect.height()
        )

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):
        model.setData(index, editor.text(), Qt.EditRole)

    @staticmethod
    def paint_line(painter: QtGui.QPainter, color: QColor, x, y, w, h):
        painter.setPen(color)
        painter.drawLine(x, y, w, h)

    @staticmethod
    def paint_text(painter: QtGui.QPainter, text: str, color: QColor, options, x, y, w, h):
        painter.setPen(color)
        painter.drawText(QRect(x, y, w, h), options, text)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        if not index.data():
            return super(FileItemDelegate, self).paint(painter, option, index)

        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)

        line_color = QColor("#CCCCCC")
        text_color = option.palette.color(QPalette.Normal, QPalette.Text)

        top = option.rect.top()
        bottom = option.rect.height()

        first_start = option.rect.left() + 50
        second_start = option.rect.left() + int(option.rect.width() / 2.5)
        third_start = option.rect.left() + int(option.rect.width() / 1.75)
        fourth_start = option.rect.left() + int(option.rect.width() / 1.25)
        end = option.rect.width() + option.rect.left()

        self.paint_text(
            painter, index.data().name, text_color, option.displayAlignment,
            first_start, top, second_start - first_start - 4, bottom
        )

        self.paint_line(painter, line_color, second_start - 2, top, second_start - 1, bottom)

        self.paint_text(
            painter, index.data().permissions, text_color, Qt.AlignCenter | option.displayAlignment,
            second_start, top, third_start - second_start - 4, bottom
        )

        self.paint_line(painter, line_color, third_start - 2, top, third_start - 1, bottom)

        self.paint_text(
            painter, index.data().size, text_color, Qt.AlignCenter | option.displayAlignment,
            third_start, top, fourth_start - third_start - 4, bottom
        )

        self.paint_line(painter, line_color, fourth_start - 2, top, fourth_start - 1, bottom)

        self.paint_text(
            painter, index.data().date, text_color, Qt.AlignCenter | option.displayAlignment,
            fourth_start, top, end - fourth_start, bottom
        )


class FileListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[File] = []

    def clear(self):
        self.beginResetModel()
        self.items.clear()
        self.endResetModel()

    def populate(self, files: list):
        self.beginResetModel()
        self.items.clear()
        self.items = files
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.items)

    def icon_path(self, index: QModelIndex = ...):
        file_type = self.items[index.row()].type
        if file_type == FileType.DIRECTORY:
            return Resources.icon_folder
        elif file_type == FileType.FILE:
            return Resources.icon_file
        elif file_type == FileType.LINK:
            link_type = self.items[index.row()].link_type
            if link_type == FileType.DIRECTORY:
                return Resources.icon_link_folder
            elif link_type == FileType.FILE:
                return Resources.icon_link_file
            return Resources.icon_link_file_unknown
        return Resources.icon_file_unknown

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.EditRole and value:
            data, error = FileRepository.rename(self.items[index.row()], value)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        timeout=10000,
                        title="Rename",
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                    )
                )
            Global.communicate.files__refresh.emit()
        return super(FileListModel, self).setData(index, value, role)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return self.items[index.row()]
        elif role == Qt.EditRole:
            return self.items[index.row()].name
        elif role == Qt.DecorationRole:
            return QPixmap(self.icon_path(index)).scaled(32, 32, Qt.KeepAspectRatio)
        return QVariant()


class FileExplorerWidget(QWidget):
    FILES_WORKER_ID = 300
    DOWNLOAD_WORKER_ID = 399

    def __init__(self, parent=None):
        super(FileExplorerWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout(self))

        self.toolbar = FileExplorerToolbar(self)
        self.layout().addWidget(self.toolbar)

        self.header = FileHeaderWidget(self)
        self.layout().addWidget(self.header)

        self.list = QListView(self)
        self.model = FileListModel(self.list)

        self.list.setSpacing(1)
        self.list.setModel(self.model)
        self.list.installEventFilter(self)
        self.list.doubleClicked.connect(self.open)
        self.list.setItemDelegate(FileItemDelegate(self.list))
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)
        self.list.setStyleSheet(read_string_from_file(Resources.style_file_list))
        self.list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.layout().addWidget(self.list)

        self.loading = QLabel(self)
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie(Resources.anim_loading, parent=self.loading)
        self.loading_movie.setScaledSize(QSize(48, 48))
        self.loading.setMovie(self.loading_movie)
        self.layout().addWidget(self.loading)

        self.empty_label = QLabel("Folder is empty", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #969696; border: 1px solid #969696")
        self.layout().addWidget(self.empty_label)

        self.layout().setStretch(self.layout().count() - 1, 1)
        self.layout().setStretch(self.layout().count() - 2, 1)

        self.text_view_window = None

        Global().communicate.files__refresh.connect(self.update)

    @property
    def files(self):
        if self.list and len(self.list.selectedIndexes()) > 0:
            return map(lambda index: self.model.items[index.row()], self.list.selectedIndexes())

    def update(self):
        super(FileExplorerWidget, self).update()
        worker = AsyncRepositoryWorker(
            name="Files",
            worker_id=self.FILES_WORKER_ID,
            repository_method=FileRepository.files,
            response_callback=self._async_response,
            arguments=()
        )
        if Adb.worker().work(worker):
            # First Setup loading view
            self.model.clear()
            self.list.setHidden(True)
            self.loading.setHidden(False)
            self.empty_label.setHidden(True)
            self.loading_movie.start()

            # Then start async worker
            worker.start()
            Global().communicate.path_toolbar__refresh.emit()

    def close(self) -> bool:
        Global().communicate.files__refresh.disconnect()
        return super(FileExplorerWidget, self).close()

    def _async_response(self, files: list, error: str):
        self.loading_movie.stop()
        self.loading.setHidden(True)

        if error:
            print(error, file=sys.stderr)
            if not files:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Files',
                        timeout=15000,
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                    )
                )
        if not files:
            self.empty_label.setHidden(False)
        else:
            self.list.setHidden(False)
            self.model.populate(files)
            self.list.setFocus()

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if obj == self.list and \
                event.type() == QEvent.KeyPress and \
                event.matches(QKeySequence.InsertParagraphSeparator) and \
                not self.list.isPersistentEditorOpen(self.list.currentIndex()):
            self.open(self.list.currentIndex())
        return super(FileExplorerWidget, self).eventFilter(obj, event)

    def open(self, index: QModelIndex = ...):
        if Adb.manager().open(self.model.items[index.row()]):
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
        action_rename.triggered.connect(self.rename)
        menu.addAction(action_rename)

        action_open_file = QAction('Open', self)
        action_open_file.triggered.connect(self.open_file)
        menu.addAction(action_open_file)

        action_delete = QAction('Delete', self)
        action_delete.triggered.connect(self.delete)
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
    def default_response(data, error):
        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title='Download error',
                    timeout=15000,
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                )
            )
        if data:
            Global().communicate.notification.emit(
                MessageData(
                    title='Downloaded',
                    timeout=15000,
                    body=data
                )
            )

    def rename(self):
        self.list.edit(self.list.currentIndex())

    def open_file(self):
        if not self.file.isdir:
            error, data = FileRepository.open_file(self.file)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title='File',
                        timeout=15000,
                        body=f"<span style='color: red; font-weight: 600'> {data} </span>"
                    )
                )
            else:
                self.text_view_window = TextView(self.file.name, data)
                self.text_view_window.show()

    def delete(self):
        fileNames = ', '.join(map(lambda f: f.name, self.files))
        reply = QMessageBox.critical(
            self,
            'Delete',
            f"Do you want to delete '{fileNames}'? It cannot be undone!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for file in self.files:
                data, error = FileRepository.delete(file)
                if data:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=10000,
                            title="Delete",
                            body=data,
                        )
                    )
                if error:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=10000,
                            title="Delete",
                            body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                        )
                    )
            Global.communicate.files__refresh.emit()

    def download(self):
        self.download_files()

    def download_to(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
        if dir_name:
            self.download_files(dir_name)

    def download_files(self, destination: str=None):
        for file in self.files:
            helper = ProgressCallbackHelper()
            worker = AsyncRepositoryWorker(
                worker_id=self.DOWNLOAD_WORKER_ID,
                name="Download",
                repository_method=FileRepository.download_to,
                response_callback=self.default_response,
                arguments=(
                    helper.progress_callback.emit, file.path, destination
                )
            )
            if Adb.worker().work(worker):
                Global().communicate.notification.emit(
                    MessageData(
                        title="Downloading to",
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=worker.set_loading_widget
                    )
                )
                helper.setup(worker, worker.update_loading_widget)
                worker.start()

    def file_properties(self):
        file, error = FileRepository.file(self.file.path)
        file = file if file else self.file

        if error:
            Global().communicate.notification.emit(
                MessageData(
                    timeout=10000,
                    title="Opening folder",
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                )
            )

        info = f"<br/><u><b>{str(file)}</b></u><br/>"
        info += f"<pre>Name:        {file.name or '-'}</pre>"
        info += f"<pre>Owner:       {file.owner or '-'}</pre>"
        info += f"<pre>Group:       {file.group or '-'}</pre>"
        info += f"<pre>Size:        {file.size or '-'}</pre>"
        info += f"<pre>Permissions: {file.permissions or '-'}</pre>"
        info += f"<pre>Date:        {file.date__raw or '-'}</pre>"
        info += f"<pre>Type:        {file.type or '-'}</pre>"

        if file.type == FileType.LINK:
            info += f"<pre>Links to:    {file.link or '-'}</pre>"

        properties = QMessageBox(self)
        properties.setStyleSheet("background-color: #DDDDDD")
        properties.setIconPixmap(
            QPixmap(self.model.icon_path(self.list.currentIndex())).scaled(128, 128, Qt.KeepAspectRatio)
        )
        properties.setWindowTitle('Properties')
        properties.setInformativeText(info)
        properties.exec_()


class TextView(QMainWindow):
    def __init__(self, filename, data):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(500, 300))    
        self.setWindowTitle(filename) 

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.insertPlainText(data)
        # self.text_edit.setDisabled(True)
        self.text_edit.move(10,10)