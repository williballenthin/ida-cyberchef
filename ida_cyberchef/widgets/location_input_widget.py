"""Widget for address and length input in FROM_LOCATION mode."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class LocationInputWidget(QWidget):
    """Widget for inputting location parameters (address and length).

    Layout:
    ┌─────────────────────────────────────────────────┐
    │ Address: [0x00401000          ] Length: [256  ] │
    └─────────────────────────────────────────────────┘
    """

    location_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Address:"))

        self._address_edit = QLineEdit()
        self._address_edit.setPlaceholderText("0x00000000")
        self._address_edit.setStyleSheet(
            "font-family: 'Courier New', Courier, monospace;"
        )
        self._address_edit.setMinimumWidth(120)
        layout.addWidget(self._address_edit)

        layout.addWidget(QLabel("Length:"))

        self._length_edit = QLineEdit()
        self._length_edit.setPlaceholderText("256")
        self._length_edit.setMinimumWidth(80)
        layout.addWidget(self._length_edit)

        layout.addStretch()

    def _connect_signals(self):
        """Connect signals and slots."""
        self._address_edit.editingFinished.connect(self._on_params_changed)
        self._length_edit.editingFinished.connect(self._on_params_changed)

    def _on_params_changed(self):
        """Handle parameter changes with validation."""
        address_text = self._address_edit.text().strip()
        length_text = self._length_edit.text().strip()

        if not address_text or not length_text:
            return

        try:
            if address_text.startswith("0x") or address_text.startswith("0X"):
                address = int(address_text, 16)
            else:
                address = int(address_text, 16)

            length = int(length_text, 10)

            if length <= 0:
                return

            self.location_changed.emit(address, length)
        except ValueError:
            pass

    def set_location(self, address: int, length: int):
        """Set address and length fields programmatically.

        Args:
            address: Effective address
            length: Number of bytes
        """
        self._address_edit.setText(f"0x{address:08x}")
        self._length_edit.setText(str(length))
