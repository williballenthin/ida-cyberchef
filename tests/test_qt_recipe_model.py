from PySide6.QtCore import Qt

from ida_cyberchef.core.recipe_models import OperationStep, RecipeDefinition
from ida_cyberchef.qt_models.recipe_model import RecipeModel


def test_create_empty_model():
    model = RecipeModel()

    assert model.rowCount() == 0


def test_add_operation():
    model = RecipeModel()
    model.add_operation("To Hex", {})

    assert model.rowCount() == 1
    index = model.index(0, 0)
    assert model.data(index, Qt.DisplayRole) == "To Hex"


def test_remove_operation():
    model = RecipeModel()
    model.add_operation("To Hex", {})
    model.add_operation("XOR", {"key": "test"})

    model.remove_operation(0)
    assert model.rowCount() == 1


def test_get_recipe_steps():
    model = RecipeModel()
    model.add_operation("To Hex", {})
    model.add_operation("XOR", {"key": "test"})

    steps = model.get_recipe_steps()
    assert len(steps) == 2
    assert steps[0]["operation"] == "To Hex"
    assert steps[1]["operation"] == "XOR"


def test_to_recipe_definition():
    model = RecipeModel()
    model.add_operation("To Hex", {})

    recipe = model.to_recipe_definition()
    assert isinstance(recipe, RecipeDefinition)
    assert len(recipe.steps) == 1


def test_from_recipe_definition():
    recipe = RecipeDefinition(
        steps=[
            OperationStep(operation="To Hex", args={}),
            OperationStep(operation="XOR", args={"key": "test"}),
        ]
    )

    model = RecipeModel()
    model.from_recipe_definition(recipe)

    assert model.rowCount() == 2
