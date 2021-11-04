import sys

from PyQt5.QtWidgets import QApplication

from services.shell import adb
from gui.window import MainWindow

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
