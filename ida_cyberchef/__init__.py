"""IDA CyberChef integration package.

This package provides CyberChef data transformation capabilities for IDA Pro
through both a Qt widget interface and a programmatic API.
"""

# Core CyberChef API (always available)
from ida_cyberchef.cyberchef import (
    DishType,
    bake,
    get_chef,
    load_cyberchef,
    plate,
)

# Input parsing
from ida_cyberchef.core.input_parser import InputFormat

# Operation registry
from ida_cyberchef.core.operation_registry import OperationRegistry

# Recipe data structures
from ida_cyberchef.core.recipe_models import OperationStep, RecipeDefinition

__all__ = [
    # Core CyberChef API
    "bake",
    "get_chef",
    "load_cyberchef",
    "plate",
    "DishType",
    # Enums
    "InputFormat",
    # Recipe structures
    "RecipeDefinition",
    "OperationStep",
    # Registry
    "OperationRegistry",
]

# Qt-dependent imports (optional - only if Qt is available)
try:
    from ida_cyberchef.cyberchef_widget import CyberChefWidget
    from ida_cyberchef.qt_models.execution_model import ExecutionModel
    from ida_cyberchef.qt_models.input_model import InputModel, InputSource
    from ida_cyberchef.qt_models.recipe_model import RecipeModel

    __all__.extend([
        "CyberChefWidget",
        "InputModel",
        "RecipeModel",
        "ExecutionModel",
        "InputSource",
    ])
except ImportError:
    # Qt not available (headless environment)
    pass
