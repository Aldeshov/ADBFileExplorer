from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

from config import Resource


class LoadingWidget(QWidget):
    def __init__(self, parent, text):
        super(LoadingWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.gif = QLabel(self)
        self.movie = QMovie(Resource.anim_loading)
        self.movie.setScaledSize(QSize(96, 96))
        self.gif.setAlignment(Qt.AlignCenter)
        self.gif.setMovie(self.movie)
        self.layout.addWidget(self.gif)
        self.movie.start()

        self.text = QLabel(self)
        self.text.setText(text)
        self.text.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.text)

        self.setFixedWidth(192)
        self.setFixedHeight(192)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(QtCore.Qt.Dialog | Qt.Window | Qt.CustomizeWindowHint)
