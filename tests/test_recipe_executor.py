from ida_cyberchef.core.recipe_executor import RecipeExecutor


def test_execute_single_operation():
    executor = RecipeExecutor()

    recipe = [{"operation": "To Hex", "args": {}}]
    results = executor.execute_recipe(b"hello", recipe)

    assert len(results) == 1
    assert results[0].success is True
    assert results[0].data is not None
    assert results[0].error is None


def test_execute_chained_operations():
    executor = RecipeExecutor()

    recipe = [
        {"operation": "To Hex", "args": {}},
        {"operation": "To Upper case", "args": {}},
    ]
    results = executor.execute_recipe(b"test", recipe)

    assert len(results) == 2
    assert all(r.success for r in results)


def test_execution_stops_on_error():
    executor = RecipeExecutor()

    recipe = [
        {"operation": "To Hex", "args": {}},
        {"operation": "InvalidOp", "args": {}},
        {"operation": "To Upper case", "args": {}},
    ]
    results = executor.execute_recipe(b"test", recipe)

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is False
    assert results[1].error is not None


def test_empty_recipe_returns_empty_list():
    executor = RecipeExecutor()

    recipe: list[dict[str, object]] = []
    results = executor.execute_recipe(b"hello", recipe)

    assert len(results) == 0


def test_step_result_holds_string_data():
    from ida_cyberchef.core.recipe_executor import StepResult

    result = StepResult(success=True, data="hello world", error=None)
    assert result.data == "hello world"
    assert isinstance(result.data, str)


def test_step_result_holds_bytes_data():
    from ida_cyberchef.core.recipe_executor import StepResult

    result = StepResult(success=True, data=b"hello world", error=None)
    assert result.data == b"hello world"
    assert isinstance(result.data, bytes)


def test_recipe_executor_preserves_string_output():
    """Verify RecipeExecutor preserves str output from bake()."""
    executor = RecipeExecutor()
    # To Base64 returns string
    recipe = [{"operation": "To Base64", "args": {}}]
    results = executor.execute_recipe(b"test", recipe)

    assert len(results) == 1
    assert results[0].success
    assert isinstance(results[0].data, str)
    assert results[0].data == "dGVzdA=="  # "test" in base64


def test_recipe_executor_preserves_bytes_output():
    """Verify RecipeExecutor preserves bytes output from bake()."""
    executor = RecipeExecutor()
    # From Base64 returns bytes
    recipe = [{"operation": "From Base64", "args": {}}]
    results = executor.execute_recipe(b"dGVzdA==", recipe)

    assert len(results) == 1
    assert results[0].success
    assert isinstance(results[0].data, bytes)
    assert results[0].data == b"test"
