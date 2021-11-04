from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QFileDialog, QStatusBar

from gui.explorer.main import Explorer
from services.filesystem.config import Asset
from services.manager import FileManager


class StatusBar(QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()

    def message(self, st, msg):
        self.showMessage(st + " :  " + msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.explorer = Explorer()
        self.setStatusBar(StatusBar())
        self.toolbar = None
        self.initial()

    def setup_menubar(self):
        # Setup actions in Menu Bar
        exit_action = QAction(QIcon(Asset.icon_exit), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('HINT :  Exit application')
        exit_action.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

    def setup_toolbar(self):
        # Setup actions in Tool Bar
        open_file = QAction(QIcon(Asset.icon_plus), 'Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('HINT :  Open new File')
        open_file.triggered.connect(self.show_dialog)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(open_file)

        up_directory = QAction(QIcon(Asset.icon_up), 'Up', self)
        up_directory.setShortcut('Escape')
        up_directory.setStatusTip('HINT :  Parent directory')
        up_directory.triggered.connect(self.action_up)
        self.toolbar = self.addToolBar('Up')
        self.toolbar.addAction(up_directory)

    def initial(self):
        self.setup_menubar()
        self.setup_toolbar()
        self.setCentralWidget(self.explorer)

        self.setMinimumWidth(480)
        self.setMinimumHeight(360)

        self.move(300, 300)
        self.resize(640, 480)
        self.setWindowIcon(QIcon(Asset.logo))
        self.setWindowTitle('ADB File Explorer')

        self.statusBar().message('INFO', 'Ready')

    def show_dialog(self):
        name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        try:
            if not name:
                self.statusBar().message('INFO', 'File not selected')
        except FileNotFoundError:
            self.statusBar().message('ERROR', 'File not found')

    def action_up(self):
        if FileManager.up():
            self.explorer.scroll.widget().update()

    def closeEvent(self, event):
        # adb.kill_server()

        # close window
        event.accept()
