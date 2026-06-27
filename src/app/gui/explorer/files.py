# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import sys
import tempfile
import webbrowser
from typing import Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QModelIndex, QAbstractListModel, QVariant, QRect, QSize, QEvent, QObject, QUrl, QThreadPool
from PyQt5.QtGui import QPixmap, QColor, QPalette, QKeySequence, QDesktopServices
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog, QStyle, QWidget, QStyledItemDelegate, \
    QStyleOptionViewItem, QApplication, QListView, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QTextEdit, \
    QMainWindow

from app.core.configurations import Resources, Settings
from app.core.main import Adb
from app.core.managers import Global, ADBManager
from app.data.models import FileType, MessageData, MessageType
from app.data.repositories import FileRepository
from app.gui.explorer.toolbar import ParentButton, UploadTools, PathBar
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper, read_string_from_file, ThumbnailWorker
from app.gui.widgets.circular_progress import CircularProgress
from app.services import stream_server


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

        self.setStyleSheet(read_string_from_file(Resources.style_file_header))


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

        # Use palette-based divider color instead of hardcoded hex
        line_color = option.palette.color(QPalette.Mid)
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
        self.items = []
        self._thumb_cache = {}    # path -> QPixmap
        self._thumb_pending = set()  # paths currently being fetched
        Global.communicate.thumbnail_ready.connect(self._on_thumbnail_ready)

    def clear(self):
        self.beginResetModel()
        self.items.clear()
        self.endResetModel()

    def populate(self, files: list):
        self.beginResetModel()
        self.items.clear()
        self._thumb_cache.clear()
        self._thumb_pending.clear()
        self.items = files
        self.endResetModel()

    def _on_thumbnail_ready(self, path: str, jpeg: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(jpeg)
        if not pixmap.isNull():
            self._thumb_cache[path] = pixmap.scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._thumb_pending.discard(path)
            # Find row and emit dataChanged
            for row, item in enumerate(self.items):
                if item.path == path:
                    idx = self.index(row, 0)
                    self.dataChanged.emit(idx, idx, [Qt.DecorationRole])
                    break

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
                        body=str(error),
                        message_type=MessageType.ERROR_MESSAGE,
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
            file = self.items[index.row()]
            if file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                if file.path in self._thumb_cache:
                    return self._thumb_cache[file.path]
                if file.path not in self._thumb_pending:
                    device = ADBManager.get_device()
                    if device:
                        self._thumb_pending.add(file.path)
                        mtime_iso = file.raw_date.isoformat() if file.raw_date else ""
                        worker = ThumbnailWorker(device.id, file.path, mtime_iso)
                        QThreadPool.globalInstance().start(worker)
            return QPixmap(self.icon_path(index)).scaled(32, 32, Qt.KeepAspectRatio)
        return QVariant()


class DeviceInfoBar(QWidget):
    """Thin bar above file list showing device model, free space, and SD-card shortcut."""

    def __init__(self, parent=None):
        super(DeviceInfoBar, self).__init__(parent)
        self._sd_path = ''
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)

        self.model_label = QLabel('', self)
        self.model_label.setStyleSheet('font-weight: bold;')
        layout.addWidget(self.model_label)

        layout.addStretch(1)

        self.storage_label = QLabel('', self)
        layout.addWidget(self.storage_label)

        from PyQt5.QtWidgets import QPushButton
        self.sd_button = QPushButton('SD card', self)
        self.sd_button.setVisible(False)
        self.sd_button.setFlat(True)
        self.sd_button.setStyleSheet('color: #4a90d9; text-decoration: underline; border: none; padding: 0 4px;')
        self.sd_button.clicked.connect(self._go_sd)
        layout.addWidget(self.sd_button)

        Global().communicate.device_info_ready.connect(self._update)
        self.setLayout(layout)

    def _update(self, model: str, avail: float, total: float, sd_path: str):
        self._sd_path = sd_path
        self.model_label.setText(model or '')
        if total > 0:
            self.storage_label.setText('%.1f GB free / %.1f GB' % (avail, total))
        else:
            self.storage_label.setText('')
        self.sd_button.setVisible(bool(sd_path))

    def _go_sd(self):
        if not self._sd_path:
            return
        file, error = FileRepository.file(self._sd_path)
        if file and Adb.manager().go(file):
            Global().communicate.files__refresh.emit()


class FileExplorerWidget(QWidget):
    FILES_WORKER_ID = 300
    DOWNLOAD_WORKER_ID = 399

    def __init__(self, parent=None):
        super(FileExplorerWidget, self).__init__(parent)
        self.main_layout = QVBoxLayout(self)

        self.toolbar = FileExplorerToolbar(self)
        self.main_layout.addWidget(self.toolbar)

        self.device_info_bar = DeviceInfoBar(self)
        self.main_layout.addWidget(self.device_info_bar)

        self.header = FileHeaderWidget(self)
        self.main_layout.addWidget(self.header)

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

        self.loading = CircularProgress(size=48, thickness=3, parent=self)
        self.loading.setVisible(False)
        self.main_layout.addWidget(self.loading, alignment=Qt.AlignCenter)

        self.empty_label = QLabel("Folder is empty", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(read_string_from_file(Resources.style_empty_label))
        self.layout().addWidget(self.empty_label)

        self.main_layout.setStretch(self.layout().count() - 1, 1)
        self.main_layout.setStretch(self.layout().count() - 2, 1)

        self.text_view_window = None
        self.setLayout(self.main_layout)

        Global().communicate.files__refresh.connect(self.update)

    @property
    def file(self):
        if self.list and self.list.currentIndex():
            return self.model.items[self.list.currentIndex().row()]

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
            self.loading.start()

            # Then start async worker
            worker.start()
            Global().communicate.path_toolbar__refresh.emit()

    def close(self) -> bool:
        Global().communicate.files__refresh.disconnect()
        return super(FileExplorerWidget, self).close()

    def _async_response(self, files: list, error: str):
        self.loading.stop()
        self.loading.setHidden(True)

        if error:
            print(error, file=sys.stderr)
            if not files:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Files',
                        timeout=15000,
                        body=str(error),
                        message_type=MessageType.ERROR_MESSAGE,
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
        action_download.triggered.connect(self.download_files)
        menu.addAction(action_download)

        action_download_to = QAction('Download to...', self)
        action_download_to.triggered.connect(self.download_to)
        menu.addAction(action_download_to)

        if self.file and not self.file.isdir:
            action_stream = QAction('Stream', self)
            action_stream.triggered.connect(self.stream_file)
            menu.addAction(action_stream)

            action_copy_stream = QAction('Copy stream link', self)
            action_copy_stream.triggered.connect(self.copy_stream_link)
            menu.addAction(action_copy_stream)

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
                    body=str(error),
                    message_type=MessageType.ERROR_MESSAGE,
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
            temp_dir = os.path.join(tempfile.gettempdir(), 'adbfe_open')
            os.makedirs(temp_dir, exist_ok=True)
            local_path = os.path.join(temp_dir, self.file.name)

            def open_response(data, error):
                if error:
                    Global().communicate.notification.emit(
                        MessageData(
                            title='Open error',
                            timeout=15000,
                            body=str(error),
                            message_type=MessageType.ERROR_MESSAGE,
                        )
                    )
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(local_path))

            helper = ProgressCallbackHelper()
            worker = AsyncRepositoryWorker(
                worker_id=self.DOWNLOAD_WORKER_ID,
                name="Open",
                repository_method=FileRepository.download,
                response_callback=open_response,
                arguments=(
                    helper.progress_callback.emit, self.file.path, temp_dir
                )
            )
            if Adb.worker().work(worker):
                Global().communicate.notification.emit(
                    MessageData(
                        title="Opening",
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=worker.set_loading_widget
                    )
                )
                helper.setup(worker, worker.update_loading_widget)
                worker.start()

    def delete(self):
        file_names = ', '.join(map(lambda f: f.name, self.files))
        reply = QMessageBox.critical(
            self,
            'Delete',
            "Do you want to delete '%s'? It cannot be undone!" % file_names,
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
                            body=str(error),
                            message_type=MessageType.ERROR_MESSAGE,
                        )
                    )
            Global.communicate.files__refresh.emit()

    def download_to(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
        if dir_name:
            self.download_files(dir_name)

    def download_files(self, destination: str = None):
        for file in self.files:
            helper = ProgressCallbackHelper()
            worker = AsyncRepositoryWorker(
                worker_id=self.DOWNLOAD_WORKER_ID,
                name="Download",
                repository_method=FileRepository.download,
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

    def _get_stream_url(self):
        """Start (or reuse) a stream server for the selected file and return the URL."""
        device = ADBManager.get_device()
        if not device:
            raise RuntimeError("No device connected")
        adb_path = Settings.adb_path()
        return stream_server.start_stream(adb_path, device.id, self.file.path)

    def stream_file(self):
        try:
            url = self._get_stream_url()
            webbrowser.open(url)
        except Exception as e:
            print("Stream error: %s" % e, file=sys.stderr)

    def copy_stream_link(self):
        try:
            url = self._get_stream_url()
            QApplication.clipboard().setText(url)
        except Exception as e:
            print("Copy stream link error: %s" % e, file=sys.stderr)

    def file_properties(self):
        file, error = FileRepository.file(self.file.path)
        file = file if file else self.file

        if error:
            Global().communicate.notification.emit(
                MessageData(
                    timeout=10000,
                    title="Opening folder",
                    body=str(error),
                    message_type=MessageType.ERROR_MESSAGE,
                )
            )

        info = "<br/><u><b>%s</b></u><br/>" % str(file)
        info += "<pre>Name:        %s</pre>" % file.name or '-'
        info += "<pre>Owner:       %s</pre>" % file.owner or '-'
        info += "<pre>Group:       %s</pre>" % file.group or '-'
        info += "<pre>Size:        %s</pre>" % file.raw_size or '-'
        info += "<pre>Permissions: %s</pre>" % file.permissions or '-'
        info += "<pre>Date:        %s</pre>" % file.raw_date or '-'
        info += "<pre>Type:        %s</pre>" % file.type or '-'

        if file.type == FileType.LINK:
            info += "<pre>Links to:    %s</pre>" % file.link or '-'

        properties = QMessageBox(self)
        properties.setStyleSheet(read_string_from_file(Resources.style_properties_dialog))
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
        self.text_edit.move(10, 10)
