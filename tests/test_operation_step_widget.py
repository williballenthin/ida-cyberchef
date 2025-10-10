"""Tests for OperationStepWidget."""

from ida_cyberchef.core.operation_registry import OperationRegistry
from ida_cyberchef.widgets.operation_step_widget import OperationStepWidget


def test_option_dropdown_shows_all_choices(qtbot):
    """Option dropdown should show all choices from schema, not just selected value."""
    registry = OperationRegistry()
    xor_op = registry.find_operation("XOR")
    assert xor_op is not None

    # Simulate saved step with "Output differential" selected
    op_with_saved = xor_op.copy()
    for arg in op_with_saved["args"]:
        if arg["name"] == "Scheme":
            arg["saved_value"] = "Output differential"

    widget = OperationStepWidget(0, op_with_saved)
    qtbot.addWidget(widget)

    # Find the Scheme dropdown
    scheme_widget = widget._arg_widgets["Scheme"]

    # Should have all 4 options
    assert scheme_widget.count() == 4
    assert scheme_widget.itemText(0) == "Standard"
    assert scheme_widget.itemText(1) == "Input differential"
    assert scheme_widget.itemText(2) == "Output differential"
    assert scheme_widget.itemText(3) == "Cascade"

    # Should have "Output differential" selected
    assert scheme_widget.currentText() == "Output differential"


def test_togglestring_dict_value_displays_correctly(qtbot):
    """ToggleString with dict value should extract string part for display."""
    registry = OperationRegistry()
    xor_op = registry.find_operation("XOR")
    assert xor_op is not None

    # Simulate saved step with toggleString dict value
    op_with_saved = xor_op.copy()
    for arg in op_with_saved["args"]:
        if arg["name"] == "Key":
            arg["value"] = {"string": "deadbeef", "option": "Hex"}

    widget = OperationStepWidget(0, op_with_saved)
    qtbot.addWidget(widget)

    # Find the Key input (it's a container with properties)
    key_container = widget._arg_widgets["Key"]
    value_input = key_container.property("value_input")
    format_combo = key_container.property("format_combo")

    # Should extract "deadbeef" for input, "Hex" for dropdown
    assert value_input.text() == "deadbeef"
    assert format_combo.currentText() == "Hex"
