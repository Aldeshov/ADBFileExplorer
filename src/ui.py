from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPaintEvent, QPixmap
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, \
    QStyleOption, QStyle, QScrollArea

from drivers import get_files
from models import File, FileTypes

PATH = []
HISTORY = []


def path():
    if not PATH:
        return '/'

    result = ''
    for p in PATH:
        result += '/'
        result += p
    return result


class StatusMessage:
    def __init__(self, st, msg):
        self.status = st
        self.message = msg

    def __str__(self):
        return self.status + ":   " + self.message

    def get(self):
        return self.__str__()


class FileListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.files_widgets = []
        self.load_list()

    def update(self):
        super().update()
        self.load_list()

    def load_list(self):
        for widget in self.files_widgets:
            self.layout.removeWidget(widget)

        self.files_widgets = []
        files = get_files(path())
        if not files:
            self.load_empty()

        for file in files:
            item = FileItemWidget(file)
            self.files_widgets.append(item)
            self.layout.insertWidget(self.layout.count() - 1, item)

    def load_empty(self):
        vertical = QVBoxLayout()
        vertical.addWidget(QLabel("Folder empty"))
        vertical.addStretch()
        horizontal = QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(vertical)
        horizontal.addStretch()
        widget = QWidget()
        widget.setStyleSheet("color: #969696")
        widget.setLayout(horizontal)
        self.files_widgets.append(widget)
        self.layout.addWidget(widget)
        return


class FileItemWidget(QWidget):
    def __init__(self, file: File):
        super().__init__()
        self.file = file
        self.installEventFilter(self)
        self.setObjectName("file")
        self.setMinimumHeight(40)
        self.style__default()
        box = QHBoxLayout()
        box.addWidget(self.file_icon)
        box.addWidget(QLabel(self.file.name))
        box.addWidget(QLabel(self.file.permissions))
        box.addWidget(QLabel(self.file.size))
        box.addWidget(QLabel(self.file.date))
        if self.file.type == FileTypes.LINK:
            self.setToolTip(self.file.link)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        self.setLayout(box)

    def style__default(self):
        self.setStyleSheet("background-color: #E6E6E6;")

    def style__hover(self):
        self.setStyleSheet("background-color: #D6D6D6;")

    def style__clicked(self):
        self.setStyleSheet("background-color: #C1C1C1;")

    @property
    def file_icon(self):
        icon = "assets/icons/files/file_unknown.png"
        if self.file.type == FileTypes.DIRECTORY:
            icon = "assets/icons/files/folder.png"
        elif self.file.type == FileTypes.FILE:
            icon = "assets/icons/files/file.png"
        elif self.file.type == FileTypes.LINK:
            if self.file.link_type == FileTypes.DIRECTORY:
                icon = "assets/icons/files/link_folder.png"
            elif self.file.link_type == FileTypes.FILE:
                icon = "assets/icons/files/link_file.png"
            else:
                icon = "assets/icons/files/link_file_unknown.png"
        pixmap = QPixmap(icon)
        pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio)
        label = QLabel()
        label.setPixmap(pixmap)
        return label

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QtCore.QEvent.HoverEnter:
            self.style__hover()
        if obj == self and event.type() == QtCore.QEvent.MouseButtonPress:
            self.style__clicked()
        if obj == self and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.style__hover()
        return super(FileItemWidget, self).eventFilter(obj, event)

    def leaveEvent(self, e):
        self.style__default()

    def paintEvent(self, event: QPaintEvent):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement(), option, painter, self)

    def mouseReleaseEvent(self, event):
        global PATH
        if self.file.type == FileTypes.DIRECTORY:
            PATH.append(self.file.name)
            self.parent().update()
        elif self.file.link_type == FileTypes.DIRECTORY:
            if self.file.link[0] == '/':
                PATH = self.file.link.split('/')
                PATH.remove('')
            else:
                for p in self.file.link.split('/'):
                    PATH.append(p)
            self.parent().update()


class Header(QWidget):
    def __init__(self):
        super().__init__()
        box = QHBoxLayout()
        box.addWidget(QLabel(""))
        box.addWidget(QLabel("File"))
        box.addWidget(QLabel("Permissions"))
        box.addWidget(QLabel("Size"))
        box.addWidget(QLabel("Created at"))
        box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(box)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.body = QWidget()
        self.header = Header()
        self.scroll = QScrollArea(self)
        self.toolbar = None
        self.progressbar = None
        self.timer = None
        self.step = 0
        self.initial()

    def setup_menubar(self):
        # Setup actions in Menu Bar
        exit_action = QAction(QIcon('assets/icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

    def setup_toolbar(self):
        # Setup actions in Tool Bar
        open_file = QAction(QIcon('assets/icons/plus.png'), 'Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open new File')
        open_file.triggered.connect(self.show_dialog)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(open_file)

        up_directory = QAction(QIcon('assets/icons/up.png'), 'Up', self)
        up_directory.setShortcut('Escape')
        up_directory.setStatusTip('Parent directory')
        up_directory.triggered.connect(self.up_directory)
        self.toolbar = self.addToolBar('Up')
        self.toolbar.addAction(up_directory)

    def initial(self):
        self.setup_menubar()
        self.setup_toolbar()

        self.scroll.setLineWidth(self.width())
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(FileListWidget())
        self.header.setMaximumHeight(24)
        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addWidget(self.scroll)
        self.body.setLayout(layout)

        self.setCentralWidget(self.body)

        self.statusBar()
        self.setMinimumHeight(360)
        self.setMinimumWidth(480)
        self.resize(640, 480)
        self.move(300, 300)
        self.setWindowTitle('File Explorer (ADB)')
        self.setWindowIcon(QIcon('../assets/logo.png'))

        self.statusBar().showMessage(StatusMessage('INFO', 'Ready').get())

    def keyPressEvent(self, e):
        self.statusBar().showMessage(StatusMessage('INFO', f'{str(e.key())} was pressed').get())

    def show_dialog(self):
        name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        try:
            if name:
                # f = open(name, 'r')
                pass
            else:
                self.statusBar().showMessage(StatusMessage('INFO', 'File not selected').get())
                self.statusBar().showMessage(StatusMessage('INFO', 'File not selected').get())
        except FileNotFoundError:
            self.statusBar().showMessage(StatusMessage('ERROR', 'File not found').get())

    def up_directory(self):
        global PATH
        if PATH:
            PATH.pop()
            self.scroll.widget().update()

    def timerEvent(self, e):

        if self.step >= 100:
            self.timer.stop()
            self.btn.setText('Finished')
            return

        self.step = self.step + 1
        self.progressbar.setValue(self.step)

    def do_action(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')

    def closeEvent(self, event):
        # adb.kill_server()

        # close window
        event.accept()
