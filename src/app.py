# ADB File Explorer `tool`
# Copyright (C) 2022  Azat Aldeshov azata1919@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

from PyQt5.QtWidgets import QApplication

from core.configurations import Application
from core.daemons import Adb
from gui.window import MainWindow

if __name__ == '__main__':
    print(Application.NOTICE)

    Adb()  # Start adb

    # Creating new Application
    app = QApplication(sys.argv)

    # Creating new window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
