import json
import re
from pathlib import Path


def title_to_camel(title_str: str) -> str:
    """Convert Title Case with spaces to camelCase.

    Args:
        title_str: Title Case string like 'From Base64'

    Returns:
        camelCase string like 'fromBase64'
    """
    words = title_str.split()
    if not words:
        return ""

    # First word lowercase, rest title case, remove spaces
    result = words[0].lower() + "".join(w.capitalize() for w in words[1:])
    # Remove any remaining spaces or special chars that shouldn't be in camelCase
    result = re.sub(r"[^a-zA-Z0-9]", "", result)
    return result


def format_arg(arg: dict) -> str:
    """Format an argument definition for markdown."""
    name = arg.get("name", "")
    arg_type = arg.get("type", "")
    value = arg.get("value", "")

    if arg_type == "option" and isinstance(value, list):
        options = ", ".join(f"`{v}`" for v in value[:3])
        if len(value) > 3:
            options += f" (+{len(value) - 3} more)"
        return f"  - **{name}** ({arg_type}): {options}"
    elif arg_type == "editableOption" and isinstance(value, list):
        # Handle both dict format and string format
        opt_names = []
        for v in value[:3]:
            if isinstance(v, dict):
                opt_names.append(f"`{v.get('name', '')}`")
            else:
                opt_names.append(f"`{v}`")
        options = ", ".join(opt_names)
        if len(value) > 3:
            options += f" (+{len(value) - 3} more)"
        return f"  - **{name}** ({arg_type}): {options}"
    elif arg_type == "boolean":
        return f"  - **{name}** ({arg_type}): default `{value}`"
    elif arg_type == "number":
        return f"  - **{name}** ({arg_type}): default `{value}`"
    else:
        return f"  - **{name}** ({arg_type}): default `{value}`"


def clean_html_description(desc: str) -> str:
    """Remove HTML tags from description."""
    # Remove <br> tags
    desc = desc.replace("<br><br>", "\n\n").replace("<br>", " ")
    # Remove <code> tags but keep content
    desc = re.sub(r"<code>(.*?)</code>", r"`\1`", desc)
    # Remove any other HTML tags
    desc = re.sub(r"<[^>]+>", "", desc)
    return desc.strip()


def generate_operation_doc(func_name: str, config: dict) -> str:
    """Generate markdown documentation for a single operation."""
    lines = []

    # Header
    lines.append(f"### `{func_name}()`")
    lines.append("")

    # Module
    module = config.get("module", "Unknown")
    lines.append(f"**Module:** {module}")
    lines.append("")

    # Description
    desc = clean_html_description(
        config.get("description", "No description available.")
    )
    lines.append(desc)
    lines.append("")

    # Info URL
    if info_url := config.get("infoURL"):
        lines.append(f"[More info]({info_url})")
        lines.append("")

    # Input/Output types
    input_type = config.get("inputType", "unknown")
    output_type = config.get("outputType", "unknown")
    lines.append(f"**Input:** `{input_type}` → **Output:** `{output_type}`")
    lines.append("")

    # Arguments
    if args := config.get("args"):
        lines.append("**Arguments:**")
        for arg in args:
            lines.append(format_arg(arg))
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def main():
    # Load operation list
    with open("cyberchef_operations.json") as f:
        operations = json.load(f)

    # Load operation config
    config_path = Path("deps/CyberChef/src/core/config/OperationConfig.json")
    with open(config_path) as f:
        operation_config = json.load(f)

    # Build reverse mapping: camelCase -> config_key
    # Convert each config key to camelCase and map it back
    # Use case-insensitive keys for lookup
    camel_to_config = {}
    for config_key in operation_config.keys():
        camel_name = title_to_camel(config_key)
        # Store both exact case and lowercase for flexible matching
        camel_to_config[camel_name] = config_key
        camel_to_config[camel_name.lower()] = config_key

    # Build documentation
    docs = []
    docs.append("# CyberChef Operations Reference")
    docs.append("")
    docs.append(
        f"This document lists all {len(operations)} available CyberChef operations."
    )
    docs.append("")
    docs.append("## Operations")
    docs.append("")

    mapped = 0
    unmapped = []

    for func_name in sorted(operations):
        # Look up the config key using the reverse mapping
        # Try exact match first, then case-insensitive
        config_key = camel_to_config.get(func_name) or camel_to_config.get(
            func_name.lower()
        )

        if config_key:
            config = operation_config[config_key]
            docs.append(generate_operation_doc(func_name, config))
            mapped += 1
        else:
            unmapped.append(func_name)

    # Save documentation
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    docs_path = docs_dir / "ops.md"
    with open(docs_path, "w") as f:
        f.write("\n".join(docs))

    print(f"Documentation generated: {docs_path}")
    print(f"Mapped: {mapped}/{len(operations)}")
    print(f"Unmapped: {len(unmapped)}")

    if unmapped:
        print("\nUnmapped operations (first 20):")
        for op in unmapped[:20]:
            print(f"  - {op}")


if __name__ == "__main__":
    main()
