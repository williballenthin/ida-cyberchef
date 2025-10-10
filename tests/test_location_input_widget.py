"""Tests for LocationInputWidget."""

from ida_cyberchef.widgets.location_input_widget import LocationInputWidget


def test_location_widget_has_address_field(qtbot):
    """LocationInputWidget should have address QLineEdit with proper placeholder."""
    widget = LocationInputWidget()
    qtbot.addWidget(widget)
    assert widget._address_edit is not None
    assert widget._address_edit.placeholderText() == "0x00000000"


def test_location_widget_has_length_field(qtbot):
    """LocationInputWidget should have length QLineEdit with proper placeholder."""
    widget = LocationInputWidget()
    qtbot.addWidget(widget)
    assert widget._length_edit is not None
    assert widget._length_edit.placeholderText() == "256"


def test_location_widget_emits_signal_on_valid_input(qtbot):
    """LocationInputWidget should emit location_changed signal with parsed values."""
    widget = LocationInputWidget()
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.location_changed, timeout=1000) as blocker:
        widget._address_edit.setText("0x401000")
        widget._length_edit.setText("128")
        widget._address_edit.editingFinished.emit()

    assert blocker.args == [0x401000, 128]
