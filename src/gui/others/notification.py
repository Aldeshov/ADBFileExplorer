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

from typing import Union

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QPropertyAnimation, QAbstractAnimation
from PyQt5.QtGui import QIcon, QPaintEvent, QPainter, QMovie
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QStyleOption, QStyle, \
    QGraphicsDropShadowEffect, QVBoxLayout, QScrollArea, QSizePolicy, QFrame, QGraphicsOpacityEffect, QProgressBar

from core.configurations import Resources
from data.models import MessageType
from helpers.tools import read_string_from_file


class BaseMessage(QWidget):
    def __init__(self, parent):
        super(BaseMessage, self).__init__(parent)
        self.notification_center = parent
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.header = QHBoxLayout()
        self.layout().addLayout(self.header)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

        self.setStyleSheet('QWidget { background: #d3d7cf; }')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumSize(self.sizeHint())
        self.setMinimumHeight(80)
        self.setFixedWidth(320)
        self.show()

    def paintEvent(self, event: QPaintEvent):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement(), option, painter, self)
        super().paintEvent(event)

    def set_opacity(self, opacity):
        self.opacity_effect.setOpacity(opacity)
        if opacity == 1:
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(10)
            shadow_effect.setOffset(1, 1)
            self.setGraphicsEffect(shadow_effect)

    def show(self):
        self.animation.valueChanged.connect(self.set_opacity)
        self.animation.setDirection(QAbstractAnimation.Forward)
        self.animation.start()
        return super().show()

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.notification_center.remove(self)
        self.deleteLater()
        return event.accept()

    def create_loading(self):
        gif = QLabel(self)
        movie = QMovie(Resources.anim_loading)
        movie.setScaledSize(QSize(24, 24))
        gif.setContentsMargins(5, 0, 5, 0)
        gif.setAlignment(Qt.AlignCenter)
        gif.setMovie(movie)

        self.header.addWidget(gif)
        movie.start()

    def create_title(self, text):
        title = QLabel(text, self)
        title.setAlignment(Qt.AlignVCenter)
        title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        title.setContentsMargins(5, 0, 0, 0)
        self.header.addWidget(title, 1)

    def create_close(self):
        button = QPushButton(self)
        button.setObjectName("close")
        button.setIcon(QIcon(Resources.icon_close))
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(10, 10))
        button.setStyleSheet(read_string_from_file(Resources.style_notification_button))
        button.clicked.connect(lambda: self.close() or None)
        self.header.addWidget(button)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self.setMinimumHeight(self.height())
        return event.accept()

    def default_body_message(self, message):
        body = QLabel(message, self)
        body.setWordWrap(True)
        body.setContentsMargins(15, 5, 20, 10)
        body.setStyleSheet("font-size: 14px; font-weight: normal;")
        return body


class LoadingMessage(BaseMessage):
    def __init__(self, parent: QWidget, title: str, body: Union[QWidget, str] = None):
        super(LoadingMessage, self).__init__(parent)

        self.label = None
        self.progress = None
        self.create_loading()
        self.create_title(title)
        if not body:
            self.label = QLabel("Waiting...", self)
            self.label.setWordWrap(True)
            self.label.setContentsMargins(10, 5, 10, 10)

            self.progress = QProgressBar(self)
            self.progress.setValue(0)
            self.progress.setMaximumHeight(16)
            self.progress.setAlignment(Qt.AlignCenter)

            self.layout().addWidget(self.label)
            self.layout().addWidget(self.progress)
        elif isinstance(body, QWidget):
            self.layout().addWidget(body)
        elif isinstance(body, str):
            self.layout().addWidget(self.default_body_message(body))

    def update_progress(self, title: str, progress: int):
        if self.label:
            self.label.setText(title)
        if self.progress:
            self.progress.setValue(progress)


class Message(BaseMessage):
    def __init__(self, parent: QWidget, title: str, body: Union[QWidget, str], timeout=5000):
        super(Message, self).__init__(parent)

        self.create_title(title)
        self.create_close()
        if isinstance(body, QWidget):
            self.layout().addWidget(body)
        elif isinstance(body, str):
            self.layout().addWidget(self.default_body_message(body))

        if timeout >= 1000:
            QTimer.singleShot(timeout, self.on_close)

    def on_close(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(100)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.valueChanged.connect(self.closing)
        self.animation.setDirection(QAbstractAnimation.Forward)
        self.animation.start()

    def closing(self, opacity):
        self.opacity_effect.setOpacity(opacity)
        if opacity == 0:
            self.close()


class NotificationCenter(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = QFrame(self)
        self.notifications.setLayout(QVBoxLayout(self.notifications))
        self.notifications.installEventFilter(self)
        self.notifications.layout().setSpacing(5)
        self.notifications.layout().addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.notifications)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setStyleSheet("QWidget { background: transparent; border: 0; }")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.verticalScrollBar().rangeChanged.connect(lambda x, y: self.verticalScrollBar().setValue(y))

        self.setMinimumSize(355, 20)
        self.update_position()
        self.adjustSize()
        self.show()

    def eventFilter(self, obj: QtCore.QObject, event: Union[QtCore.QEvent, QtGui.QResizeEvent]) -> bool:
        if obj == self.notifications and event.type() == event.Resize:
            if self.maximumHeight() > self.rect().height() < event.size().height():
                self.resize(self.rect().width(), event.size().height() + self.notifications.layout().spacing())

        return super(NotificationCenter, self).eventFilter(obj, event)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super(NotificationCenter, self).resizeEvent(event)
        self.update_position()

    def update_position(self):
        geometry = self.geometry()
        geometry.moveTopLeft(
            QPoint(
                self.parent().rect().width() - self.rect().width(),
                self.parent().rect().height() - self.rect().height()
            )
        )
        self.setGeometry(geometry)
        self.setMaximumHeight(self.parent().rect().height())

    def append_notification(self, title: str, body: Union[QWidget, str], timeout=0, message_type=MessageType.MESSAGE):
        if message_type == MessageType.MESSAGE:
            message = Message(self, title, body, timeout)
            self.append(message)
            return message
        elif message_type == MessageType.LOADING_MESSAGE:
            message = LoadingMessage(self, title, body)
            self.append(message)
            return message

    def append(self, message: BaseMessage):
        self.notifications.layout().addWidget(message)
        self.notifications.adjustSize()
        self.update_position()

    def remove(self, message: BaseMessage):
        self.notifications.layout().removeWidget(message)
        self.adjustSize()
        self.update_position()
