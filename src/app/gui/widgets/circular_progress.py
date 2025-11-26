from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen


class CircularProgress(QWidget):
    def __init__(self, parent=None, size=None, thickness=None):
        super().__init__(parent)
        self.angle = 0
        self.arc_length = 90
        self.growing = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)

        # Configurable size and thickness
        self._size = size or 50
        self._thickness = thickness or 4

        self.setMinimumSize(self._size, self._size)

        # Optional: Set a preferred/maximum size
        if size:
            self.setFixedSize(size, size)

    def start(self):
        self.timer.start(20)

    def stop(self):
        self.timer.stop()

    def setSize(self, size):
        """Dynamically change the size"""
        self._size = size
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
        self.update()

    def setThickness(self, thickness):
        """Dynamically change the line thickness"""
        self._thickness = thickness
        self.update()

    def animate(self):
        self.angle = (self.angle + 5) % 360

        # Pulsing arc effect
        if self.growing:
            self.arc_length += 2
            if self.arc_length >= 320:
                self.growing = False
        else:
            self.arc_length -= 2
            if self.arc_length <= 30:
                self.growing = True

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Use theme color
        color = self.palette().highlight().color()
        pen = QPen(color)

        # Scale thickness based on widget size
        scaled_thickness = max(2, int(self._thickness * min(self.width(), self.height()) / self._size))
        pen.setWidth(scaled_thickness)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Draw arc - scales automatically with widget size
        side = min(self.width(), self.height())
        margin = scaled_thickness + 2
        rect_size = side - (margin * 2)
        x = (self.width() - rect_size) / 2
        y = (self.height() - rect_size) / 2

        painter.drawArc(int(x), int(y), rect_size, rect_size,
                        self.angle * 16, self.arc_length * 16)
