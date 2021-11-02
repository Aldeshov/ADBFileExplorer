import sys

from PyQt5.QtWidgets import QApplication

from services.shell import adb
from ui import MainWindow

DEVICE_ID = '192.168.8.1'

if __name__ == '__main__':
    validation = adb.validate()
    message = "adb not found!\nPlease check 'bin' folder or replace necessary adb files to 'bin/'"
    assert validation, message

    adb.start_server()
    adb.connect(DEVICE_ID)

    app = QApplication(sys.argv)
    app.setStyleSheet(
        '''
        QWidget#file {}
        FileItemWidget#file:hover {}
        QWidget#file:pressed {}
        '''
    )

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
