from PyQt5.QtGui import QIcon, QFocusEvent
from PyQt5.QtWidgets import QToolButton, QMenu, QWidget, QAction, QFileDialog, QInputDialog, QMessageBox, QLineEdit, \
    QHBoxLayout

from config import Resource
from gui.others.additional import LoadingWidget
from services.data.managers import Global, FileManager
from services.data.repositories import FileRepository


class UploadTools(QToolButton):
    def __init__(self, parent):
        super(UploadTools, self).__init__(parent)
        self.menu = QMenu(self)
        self.__error__ = ''
        self.loading: QWidget
        self.__queue__ = list()
        self.show_action = QAction(QIcon(Resource.icon_plus), 'Upload', self)
        self.show_action.triggered.connect(self.showMenu)
        self.setDefaultAction(self.show_action)

        upload_files = QAction(QIcon(Resource.icon_files_upload), '&Upload files', self)
        upload_files.triggered.connect(self.__upload_files__)
        self.menu.addAction(upload_files)

        upload_directory = QAction(QIcon(Resource.icon_folder_upload), '&Upload directory', self)
        upload_directory.triggered.connect(self.__upload_directory__)
        self.menu.addAction(upload_directory)

        upload_files = QAction(QIcon(Resource.icon_folder_create), '&Create folder', self)
        upload_files.triggered.connect(self.__create_folder__)
        self.menu.addAction(upload_files)
        self.setMenu(self.menu)

    def __upload_files__(self):
        file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]

        if file_names:
            self.loading = LoadingWidget(self, 'Uploading... Please wait')
            self.__queue__ = file_names
            self.__upload__()

    def __upload_directory__(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')

        if dir_name:
            self.loading = LoadingWidget(self, 'Uploading... Please wait')
            self.__queue__.append(dir_name)
            self.__upload__()

    def __create_folder__(self):
        text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')

        if ok:
            data, error = FileRepository.new_folder(text)
            if error:
                QMessageBox.critical(self, 'New folder', error)
            if data:
                QMessageBox.information(self, 'New folder', data)
            Global().communicate.files__refresh.emit()

    def __upload__(self, code=None, error=None):
        if error:
            self.__error__ += error

        if self.__queue__:
            FileRepository.upload(self.__queue__[0], self.__upload__)
            del self.__queue__[0]
            return True

        self.loading.close()
        del self.loading

        if self.__error__ or code != 0:
            QMessageBox.critical(self, 'Uploading', error or 'Failed to upload! Check the terminal')
            self.__error__ = ''
        else:
            QMessageBox.information(self, 'Upload', 'Successfully uploaded!')
        Global().communicate.files__refresh.emit()


class ParentButton(QToolButton):
    def __init__(self, parent):
        super(ParentButton, self).__init__(parent)
        self.parent_action = QAction(QIcon(Resource.icon_up), 'Parent', self)
        self.parent_action.triggered.connect(self.__action__)
        self.parent_action.setShortcut('Escape')
        self.setDefaultAction(self.parent_action)

    @staticmethod
    def __action__():
        if FileManager.up():
            Global().communicate.files__refresh.emit()


class PathBar(QWidget):
    class LineEdit(QLineEdit):
        def focusInEvent(self, event: QFocusEvent):
            super().focusInEvent(event)
            self.setText(FileManager.path())

    def __init__(self, parent: QWidget = 0):
        super(PathBar, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.path_text = self.LineEdit()
        self.path_text.setFixedHeight(32)
        self.path_text.returnPressed.connect(self.__action__)
        self.layout.addWidget(self.path_text)
        self.path_go = QToolButton()
        self.path_go.setFixedHeight(32)
        self.path_go.setFixedWidth(32)
        self.action = QAction(QIcon(Resource.icon_go), 'Go', self)
        self.action.triggered.connect(self.__action__)
        self.path_go.setDefaultAction(self.action)
        self.layout.addWidget(self.path_go)

        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        Global().communicate.path_toolbar__refresh.connect(self.__update__)

    def __update__(self):
        self.path_text.setText(f"{FileManager.get_device()}:{FileManager.path()}")

    def __action__(self):
        path = self.path_text.text()
        self.path_text.clearFocus()
        if path.startswith(f"{FileManager.get_device()}:"):
            path = path.replace(f"{FileManager.get_device()}:", '')

        file, error = FileRepository.file(path)
        if error:
            QMessageBox.critical(self, 'Go to folder', error)
            Global().communicate.path_toolbar__refresh.emit()
        elif file and FileManager.go(file):
            Global().communicate.files__refresh.emit()
        else:
            QMessageBox.critical(self, 'Go to folder', 'Cannot open location')
