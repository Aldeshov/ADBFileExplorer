from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QStyleOption, QStyle, QSizePolicy, QVBoxLayout, QMessageBox


class BaseResponsePopup(QWidget):
    def __init__(self):
        super().__init__()

    def show_response_status(self, response, title):
        data, error = response
        if data:
            self.show_response_successful(title, data)
        if error:
            self.show_response_error(title, error)
        if not data and not error:
            self.show_response_empty(title, 'No response got!')

    def show_response_empty(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_response_successful(self, title, message):
        QMessageBox.information(self, title, message)

    def show_response_error(self, title, message):
        QMessageBox.critical(self, title, message)


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


class BaseListItemWidget(BaseResponsePopup):
    def __init__(self):
        super().__init__()
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
        icon = BaseIconWidget(path, width=kwargs.get("width") or 25, height=kwargs.get("height") or 25)
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


class BaseListWidget(BaseResponsePopup):
    def __init__(self):
        super().__init__()
        self.widgets = []

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def load(self, widgets, empty_message="Empty", empty_full=True):
        for widget in self.widgets:
            self.layout.removeWidget(widget)
        self.widgets.clear()

        if not widgets:
            self.empty(empty_message, empty_full)
        else:
            for widget in widgets:
                self.widgets.append(widget)
                self.layout.insertWidget(self.layout.count() - 1, widget)

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
