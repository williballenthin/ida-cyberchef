import json

from ida_cyberchef.core.recipe_models import OperationStep, RecipeDefinition


def test_create_recipe_definition():
    recipe = RecipeDefinition(
        version="1.0",
        steps=[
            OperationStep(operation="To Hex", args={}),
            OperationStep(operation="XOR", args={"key": "secret"}),
        ],
    )

    assert recipe.version == "1.0"
    assert len(recipe.steps) == 2


def test_serialize_to_json():
    recipe = RecipeDefinition(
        steps=[
            OperationStep(operation="To Hex", args={}),
        ]
    )

    json_str = recipe.model_dump_json()
    data = json.loads(json_str)

    assert data["version"] == "1.0"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["operation"] == "To Hex"


def test_deserialize_from_json():
    json_data = {"version": "1.0", "steps": [{"operation": "To Hex", "args": {}}]}

    recipe = RecipeDefinition.model_validate(json_data)

    assert recipe.version == "1.0"
    assert len(recipe.steps) == 1
