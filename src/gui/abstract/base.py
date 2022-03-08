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

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap, QMovie
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QStyleOption, QStyle, QSizePolicy, QVBoxLayout, QGridLayout

from core.configurations import Resource


class BaseIconWidget(QLabel):
    def __init__(self, path, width=32, height=32, context: QWidget = None):
        super(BaseIconWidget, self).__init__()
        self.setParent(context)
        self.pixmap = QPixmap(path)
        self.pixmap = self.pixmap.scaled(width, height, Qt.KeepAspectRatio)
        self.setPixmap(self.pixmap)


class BaseListHeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    @staticmethod
    def property(label, **kwargs):
        return BaseListItemWidget.property(
            label,
            font_style=kwargs.get("font_style"),
            alignment=kwargs.get("alignment"),
            width_policy=kwargs.get("width_policy"),
            height_policy=kwargs.get("height_policy"),
            stretch=kwargs.get("stretch")
        )


class BaseListItemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setObjectName("item")
        self.installEventFilter(self)
        self.setStyleSheet("background-color: #E6E6E6;")

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def enterEvent(self, event: QtCore.QEvent):
        self.setStyleSheet("background-color: #D6D6D6;")

    def leaveEvent(self, event: QtCore.QEvent):
        self.setStyleSheet("background-color: #E6E6E6;")

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.setStyleSheet("background-color: #C1C1C1;")

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.setStyleSheet("background-color: #D6D6D6;")

    def paintEvent(self, event: QPaintEvent):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement(), option, painter, self)
        super().paintEvent(event)

    @staticmethod
    def icon(path: str, **kwargs):
        icon = BaseIconWidget(path, width=kwargs.get("width") or 28, height=kwargs.get("height") or 28)
        icon.setContentsMargins(kwargs.get("margin") or 5, 0, 0, 0)
        policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)
        icon.setSizePolicy(policy)
        return icon

    @staticmethod
    def name(label: str, **kwargs):
        name = QLabel(label)
        name.setContentsMargins(kwargs.get("margin") or 10, 0, 0, 0)
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(kwargs.get("stretch") or 4)
        name.setSizePolicy(policy)
        return name

    @staticmethod
    def property(label, **kwargs):
        prop = QLabel(label)
        if kwargs.get("font_style"):
            prop.setStyleSheet(kwargs.get("font_style"))
        if kwargs.get("alignment"):
            prop.setAlignment(kwargs.get("alignment"))

        policy = QSizePolicy(
            kwargs.get("width_policy") or QSizePolicy.Ignored,
            kwargs.get("height_policy") or QSizePolicy.Preferred
        )
        policy.setHorizontalStretch(kwargs.get("stretch") or 2)
        prop.setSizePolicy(policy)
        return prop

    @staticmethod
    def separator(width=1):
        item = QLabel()
        item.setStyleSheet("background-color: #CACACA")
        item.setMaximumWidth(width)
        return item


class BaseListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = []
        self.loading_widget = None

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def load(self, widgets, empty_message="Empty", empty_full=True):
        self.clear()

        if not widgets:
            self.empty(empty_message, empty_full)
        else:
            for widget in widgets:
                self.widgets.append(widget)
                self.layout.insertWidget(self.layout.count() - 1, widget)

    def loading(self):
        self.clear()
        gif = QLabel(self)
        movie = QMovie(Resource.anim_loading)
        movie.setScaledSize(QSize(48, 48))
        gif.setAlignment(Qt.AlignCenter)
        gif.setMovie(movie)

        box = QGridLayout()
        box.addWidget(gif, 1, 0)
        box.setAlignment(Qt.AlignCenter)

        self.loading_widget = QWidget()
        self.loading_widget.setLayout(box)
        self.widgets.append(self.loading_widget)
        self.layout.addWidget(self.loading_widget, 1)
        movie.start()

    def clear(self):
        if self.loading_widget:
            self.layout.removeWidget(self.loading_widget)
            self.loading_widget.close()
            self.loading_widget = None
        for widget in self.widgets:
            self.layout.removeWidget(widget)
            widget.close()
            widget.deleteLater()
        self.widgets.clear()

    def empty(self, msg, full):
        if full:
            label = QLabel(msg)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #969696")
            box = QVBoxLayout()
            box.addWidget(label)
            box.addStretch()

            widget = QWidget()
            widget.setLayout(box)
            self.widgets.append(widget)
            self.layout.addWidget(widget)
        else:
            label = QLabel(msg)
            label.setStyleSheet("color: #969696")
            self.layout.insertWidget(self.layout.count() - 1, label)
