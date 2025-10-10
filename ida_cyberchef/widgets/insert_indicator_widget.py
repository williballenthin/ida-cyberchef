"""Insert indicator widget for recipe panel."""

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QEnterEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget


class InsertIndicatorWidget(QWidget):
    """Widget that shows a subtle insert indicator with hover effect.

    Default state: Small gray circle with "+" on the left
    Hover state: Blue circle with "+" and blue horizontal line across width
    Both circle and line are clickable.
    """

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup widget UI with circle button and horizontal line."""
        self.setFixedHeight(17)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Horizontal line (hidden by default, positioned absolutely behind circle)
        self._line = QFrame()
        self._line.setFrameShape(QFrame.HLine)
        self._line.setFixedHeight(2)
        self._line.setStyleSheet("background-color: #2196F3;")
        self._line.setParent(self)
        self._line.setGeometry(0, 7, self.width(), 2)
        self._line.setVisible(False)

        # Circle button (positioned on top of line via absolute positioning)
        self._circle = QPushButton("+")
        self._circle.setFixedSize(17, 17)
        self._circle.setStyleSheet("""
            QPushButton {
                border: 1px solid #2196F3;
                border-radius: 8px;
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding-top: -1px;
            }
        """)
        self._circle.clicked.connect(self.clicked.emit)
        self._circle.setVisible(False)

        # Position circle absolutely at left edge
        self._circle.setParent(self)
        self._circle.move(0, 0)
        self._circle.raise_()

    def enterEvent(self, event: QEnterEvent) -> None:
        """Show highlight on hover."""
        self._line.setVisible(True)
        self._circle.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Hide highlight when not hovering."""
        self._line.setVisible(False)
        self._circle.setVisible(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Make entire widget clickable."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Update line width on resize."""
        self._line.setGeometry(0, 7, self.width(), 2)
        super().resizeEvent(event)
