"""Plain text formatter for operation documentation."""

import re


def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text and convert <br> to newlines.

    Args:
        text: Text that may contain HTML tags

    Returns: Plain text with HTML tags removed and <br> converted to \n
    """
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text


def format_operation_docs(operation: dict) -> str:
    """Format operation metadata as plain text documentation.

    Args:
        operation: Operation dict with name, category, description, args

    Returns: Formatted plain text documentation
    """
    lines = []

    lines.append(operation["name"])
    lines.append(f"Category: {operation.get('category', 'Unknown')}")
    lines.append("")

    description = operation.get("description", "No description available.")
    description = strip_html_tags(description)
    lines.append(description)
    lines.append("")

    args = operation.get("args", [])
    if not args:
        lines.append("Parameters: None")
    else:
        lines.append("Parameters:")
        for arg in args:
            arg_name = arg.get("name", "Unknown")
            arg_type = arg.get("type", "unknown")
            arg_value = arg.get("value")

            param_line = f"  {arg_name} ({arg_type})"

            if "toggleValues" in arg:
                toggle_vals = arg["toggleValues"]
                param_line += f" - Options: {', '.join(str(v) for v in toggle_vals)}"
            elif arg_value is not None and arg_value != "":
                if isinstance(arg_value, list):
                    param_line += f" - Options: {', '.join(str(v) for v in arg_value)}"
                else:
                    param_line += f" - Default: {arg_value}"

            lines.append(param_line)

    return "\n".join(lines)
