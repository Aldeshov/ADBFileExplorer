from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMenu, QAction, QGridLayout, QLabel, QWidget

from gui.abstract.base import BaseListItemWidget, BaseListWidget, BaseListHeaderWidget
from services.drivers import get_files
from services.filesystem.config import Asset
from services.manager import FileManager
from services.models import File, FileTypes


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
    def __init__(self):
        super(FileListWidget, self).__init__()
        self.files_widgets()

    def update(self):
        super(FileListWidget, self).update()
        self.files_widgets()

    def files_widgets(self):
        files = get_files(FileManager.get_device(), FileManager.path())
        widgets = []
        for file in files:
            item = FileItemWidget(file)
            widgets.append(item)
        self.load(widgets, "Folder is empty")


class FileItemWidget(BaseListItemWidget):
    def __init__(self, file: File):
        super(FileItemWidget, self).__init__()
        self.file = file
        self.properties = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

        self.layout.addWidget(
            self.icon(self.icon_path)
        )

        self.layout.addWidget(
            self.name(file.name)
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
            if self.file.link_type == FileTypes.DIRECTORY:
                return Asset.icon_link_folder
            elif self.file.link_type == FileTypes.FILE:
                return Asset.icon_link_file
            else:
                return Asset.icon_link_file_unknown
        return Asset.icon_file_unknown

    def mouseReleaseEvent(self, event):
        super(FileItemWidget, self).mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            if FileManager.open(self.file):
                self.parent().update()

    def context_menu(self, pos: QPoint):
        global_pos = self.mapToGlobal(pos)

        menu = QMenu()
        action_properties = QAction('Properties', self)
        action_properties.triggered.connect(self.file_properties)
        action_copy = QAction('Copy', self)
        action_move = QAction('Move', self)
        action_delete = QAction('Delete', self)
        action_rename = QAction('Rename', self)
        action_download = QAction('Download to', self)

        menu.addSection("Actions")
        menu.addAction(action_copy)
        menu.addAction(action_move)
        menu.addAction(action_delete)
        menu.addAction(action_rename)
        menu.addAction(action_download)
        menu.addSeparator()
        menu.addAction(action_properties)
        menu.exec(global_pos)

    def file_properties(self):
        if self.properties:
            self.properties.close()
        layout = QGridLayout()
        title = QLabel("<b>" + str(self.file) + "</b>")
        title.setToolTip(str(self.file))
        layout.addWidget(title, 1, 0)
        layout.addWidget(QLabel("Name:"), 2, 0)
        layout.addWidget(QLabel(self.file.name), 2, 1)
        layout.addWidget(QLabel("Owner:"), 3, 0)
        layout.addWidget(QLabel(self.file.owner), 3, 1)
        layout.addWidget(QLabel("Group:"), 4, 0)
        layout.addWidget(QLabel(self.file.group), 4, 1)
        layout.addWidget(QLabel("Permissions:"), 5, 0)
        layout.addWidget(QLabel(self.file.permissions), 5, 1)
        layout.addWidget(QLabel("Date:"), 6, 0)
        layout.addWidget(QLabel(self.file.date_raw), 6, 1)
        layout.addWidget(QLabel("Type:"), 7, 0)
        layout.addWidget(QLabel(self.file.type), 7, 1)

        if self.file.type == FileTypes.FILE:
            layout.addWidget(QLabel("Size:"), 8, 0)
            layout.addWidget(QLabel(self.file.size), 8, 1)
        elif self.file.type == FileTypes.LINK:
            layout.addWidget(QLabel("Links to:"), 8, 0)
            layout.addWidget(QLabel(self.file.link), 8, 1)

        self.properties = QWidget()
        self.properties.setFixedWidth(320)
        self.properties.setFixedHeight(400)
        self.properties.setLayout(layout)
        self.properties.setWindowTitle('Properties')
        self.properties.move(
            self.parent().parent().mapToGlobal(self.parent().parent().pos()).x(),
            self.parent().parent().mapToGlobal(self.parent().parent().pos()).y() - 100
        )
        self.properties.show()
        self.properties.layout().deleteLater()
