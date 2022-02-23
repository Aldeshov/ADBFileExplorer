import platform
import sys

from PyQt5.QtWidgets import QApplication

from core.configurations import Application
from core.daemons import Adb
from gui.window import MainWindow

# To convert project to executable files with py-installer
# change DEBUG in config.py to False
if __name__ == '__main__':
    print(f'ADB File explorer version {Application.VERSION}')
    print(f'Platform: {platform.platform()}')

    # Starting adb
    Adb.start()

    # Creating new Application
    app = QApplication(sys.argv)

    # Creating new window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
