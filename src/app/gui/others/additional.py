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

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

from app.core.configurations import Resources


class LoadingWidget(QWidget):
    def __init__(self, parent, text):
        super(LoadingWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.gif = QLabel(self)
        self.movie = QMovie(Resources.anim_loading)
        self.movie.setScaledSize(QSize(96, 96))
        self.gif.setAlignment(Qt.AlignCenter)
        self.gif.setMovie(self.movie)
        self.layout.addWidget(self.gif)
        self.movie.start()

        self.text = QLabel(self)
        self.text.setText(text)
        self.text.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.text)

        self.setMinimumSize(192, 192)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(QtCore.Qt.Dialog | Qt.Window | Qt.CustomizeWindowHint)

        self.show()
