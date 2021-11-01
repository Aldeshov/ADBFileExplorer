import sys

from PyQt5.QtWidgets import QApplication

from services.shell import adb
from ui import MainWindow

DEVICE_ID = '192.168.8.1'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(
        '''
        QWidget#file {}
        FileItemWidget#file:hover {}
        QWidget#file:pressed {}
        '''
    )

    adb.start_server()
    adb.connect(DEVICE_ID)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
