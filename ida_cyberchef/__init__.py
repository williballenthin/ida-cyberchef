"""IDA CyberChef integration package.

This package provides CyberChef data transformation capabilities for IDA Pro
through both a Qt widget interface and a programmatic API.
"""

# Main widget
# Input parsing
from ida_cyberchef.core.input_parser import InputFormat

# Operation registry
from ida_cyberchef.core.operation_registry import OperationRegistry

# Recipe data structures
from ida_cyberchef.core.recipe_models import OperationStep, RecipeDefinition

# Core CyberChef API
from ida_cyberchef.cyberchef import (
    DishType,
    bake,
    get_chef,
    load_cyberchef,
    plate,
)
from ida_cyberchef.cyberchef_widget import CyberChefWidget

# Qt models
from ida_cyberchef.qt_models.execution_model import ExecutionModel
from ida_cyberchef.qt_models.input_model import InputModel, InputSource
from ida_cyberchef.qt_models.recipe_model import RecipeModel

__all__ = [
    # Main widget
    "CyberChefWidget",
    # Core CyberChef API
    "bake",
    "get_chef",
    "load_cyberchef",
    "plate",
    "DishType",
    # Qt models
    "InputModel",
    "RecipeModel",
    "ExecutionModel",
    # Enums
    "InputSource",
    "InputFormat",
    # Recipe structures
    "RecipeDefinition",
    "OperationStep",
    # Registry
    "OperationRegistry",
]
