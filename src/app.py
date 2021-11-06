import sys

from PyQt5.QtWidgets import QApplication

from gui.window import MainWindow
from services.shell import adb

if __name__ == '__main__':
    # Validate ADB and start server
    adb.validate()
    adb.start_server()

    # Creating new Application
    app = QApplication(sys.argv)

    # Creating new window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
