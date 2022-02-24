from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QPropertyAnimation, QAbstractAnimation
from PyQt5.QtGui import QIcon, QPaintEvent, QPainter, QMovie
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QStyleOption, QStyle, \
    QGraphicsDropShadowEffect, QVBoxLayout, QScrollArea, QSizePolicy, QFrame, QGraphicsOpacityEffect, QProgressBar
from typing import Union

from core.configurations import Resource
from data.models import MessageData


class BaseMessage(QWidget):
    def __init__(self, parent, height=125):
        super(BaseMessage, self).__init__(parent)
        self.box = QVBoxLayout()
        self.__parent__ = parent

        self.header = QHBoxLayout()
        self.box.addLayout(self.header)
        self.box.setSpacing(0)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

        self.box.setSpacing(0)
        self.box.setContentsMargins(5, 2, 5, 2)
        self.setLayout(self.box)
        self.setStyleSheet('QWidget { background: #d3d7cf; }')
        self.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        if height < 75:
            height = 75
        self.setFixedSize(320, height)
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

    def close(self) -> bool:
        self.__parent__.notifications.layout().removeWidget(self)
        self.__parent__.resize(
            self.__parent__.rect().width(),
            self.__parent__.notifications.rect().height() - self.rect().height()
        )
        self.__parent__.update_position()
        return super(BaseMessage, self).close()

    def create_loading(self):
        gif = QLabel(self)
        movie = QMovie(Resource.anim_loading)
        movie.setScaledSize(QSize(24, 24))
        gif.setContentsMargins(5, 0, 5, 0)
        gif.setAlignment(Qt.AlignCenter)
        gif.setMovie(movie)

        self.header.addWidget(gif)
        movie.start()

    def create_title(self, text):
        title = QLabel(text, self)
        title.setObjectName("title")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setContentsMargins(5, 0, 20, 0)
        self.header.addWidget(title, 1)

    def create_close(self):
        button = QPushButton(self)
        button.setObjectName("close")
        button.setIcon(QIcon.fromTheme("window-close"))
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(16, 16))
        button.setStyleSheet(
            """
            QPushButton#close {
                background-color: #c4c8c0;
                border: 0px;
            }
            QPushButton#close:hover {
                background-color: #a6a8a3;
                border: 0px;
            }
            QPushButton#close:hover:!pressed {
              border: 1px solid #928519;
            }
            QPushButton#close:pressed {
              background-color: #928519;
            }
            """
        )
        button.clicked.connect(lambda: self.close() or None)
        self.header.addWidget(button)

    def default_body_message(self, message):
        body = QLabel(message, self)
        body.setWordWrap(True)
        body.setObjectName("body")
        body.setContentsMargins(15, 5, 15, 5)
        body.setStyleSheet(
            """
            QWidget#body {
                font-size: 14px;
                font-weight: normal;
                padding: 0;
            }
            """
        )
        return body


class LoadingMessage(BaseMessage):
    def __init__(self, parent, title: str, body: Union[QWidget, str], height=125):
        super(LoadingMessage, self).__init__(parent, height)

        self.data = 0  # For downloading // uploading data holder
        self.label = None
        self.progress = None
        self.create_loading()
        self.create_title(title)
        if isinstance(body, QWidget):
            self.body = body
        else:
            self.body = self.default_body_message(body)
        self.box.addWidget(self.body)

    def setup_progress(self):
        self.box.removeWidget(self.body)
        self.body.close()
        self.body.deleteLater()

        self.label = QLabel("Waiting...", self)
        self.label.setWordWrap(True)
        self.label.setContentsMargins(10, 0, 5, 2)
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        self.progress.setMaximumHeight(16)
        self.progress.setAlignment(Qt.AlignCenter)

        self.box.addWidget(self.label)
        self.box.addWidget(self.progress)

    def update_progress(self, title: str, progress: int):
        if self.label:
            self.label.setText(title)
        if self.progress:
            self.progress.setValue(progress)


class Message(BaseMessage):
    def __init__(self, parent, title: str, body: QWidget, timeout=5000, height=125):
        super(Message, self).__init__(parent, height)

        self.create_title(title)
        self.create_close()
        if isinstance(body, QWidget):
            self.body = body
        else:
            self.body = self.default_body_message(body)
        self.box.addWidget(self.body)

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


class MessageType:
    BASE_MESSAGE = 0
    MESSAGE = 1
    LOADING_MESSAGE = 2


class NotificationCenter(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent: QWidget = parent
        self.notifications = QFrame()
        self.notifications.setLayout(QVBoxLayout())
        self.notifications.setContentsMargins(0, 0, 0, 0)
        self.notifications.layout().addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.notifications)
        self.setContentsMargins(0, 0, 5, 5)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setStyleSheet("border: 0px; background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.setMinimumWidth(350)
        self.update_position()
        self.show()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self.update_position()
        super(NotificationCenter, self).resizeEvent(event)

    def update_position(self):
        geometry = self.geometry()
        geometry.moveTopLeft(
            QPoint(
                self.parent.rect().width() - self.rect().width() - 5,
                self.parent.rect().height() - self.rect().height() - 5
            )
        )
        self.setGeometry(geometry)
        self.setMaximumHeight(self.parent.rect().height() - 15)

    def append_notification(self, message_data: MessageData = None):
        title = message_data.title
        body = message_data.body
        timeout = message_data.timeout
        message_type = message_data.message_type
        height = message_data.height
        message_catcher = message_data.message_catcher

        if message_type == MessageType.MESSAGE:
            message = Message(self, title, body, timeout, height)
        elif message_type == MessageType.LOADING_MESSAGE:
            message = LoadingMessage(self, title, body, height)
        else:
            message = BaseMessage(self, height)
            message.create_title(title)
            message.create_close()
            if not isinstance(body, QWidget):
                body = QLabel(str(body))
                body.setContentsMargins(10, 5, 10, 5)
                body.setWordWrap(True)
            message.box.addWidget(body)

        self.notifications.layout().addWidget(message)
        self.resize(self.rect().width(), self.notifications.height() + message.rect().height())
        self.update_position()

        if message_catcher:
            message_catcher(message)
