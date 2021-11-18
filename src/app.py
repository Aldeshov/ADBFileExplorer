import platform
import sys

from PyQt5.QtWidgets import QApplication

from config import Application
from gui.window import MainWindow
from services.shell import adb


# To convert project to executable files with py-installer
# change DEBUG in config.py to False
if __name__ == '__main__':
    # Initial log
    print(f'ADB File explorer version {Application.VERSION}')
    print(f'Platform: {platform.platform()}')

    # Validate ADB and start server
    adb.validate()
    print(adb.version().OutputData)

    adb_server = adb.start_server()
    print(adb_server.OutputData or adb_server.ErrorData or 'ADB server running...')

    # Creating new Application
    app = QApplication(sys.argv)

    # Creating new window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
