import platform
import sys

from PyQt5.QtWidgets import QApplication

from core.configurations import Application
from core.daemons import Adb
from gui.window import MainWindow

if __name__ == '__main__':
    print(f'ADB File explorer version {Application.__version__}')
    print(f'Platform: {platform.platform()}')

    Adb()  # Start adb

    # Creating new Application
    app = QApplication(sys.argv)

    # Creating new window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
