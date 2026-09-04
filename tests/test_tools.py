import pytest
from orchestrator.tools.interface import BaseTool
from orchestrator.tools.registry import ToolRegistry
from orchestrator.tools.calculator import CalculatorTool, calculate, register_calculator
from orchestrator.tools import default_registry

# ---------------------------------------------------------------------------
# 1. Tool Interface Tests
# ---------------------------------------------------------------------------

class DummyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="dummy",
            description="A dummy test tool",
            metadata={"version": "1.0"}
        )

    def execute(self, message: str) -> str:
        return f"Echo: {message}"

def test_tool_interface_properties_and_execution():
    tool = DummyTool()
    assert tool.name == "dummy"
    assert tool.description == "A dummy test tool"
    assert tool.metadata == {"version": "1.0"}
    assert tool.execute("hello") == "Echo: hello"

def test_tool_interface_validation():
    class InvalidNameTool(BaseTool):
        def execute(self, *args, **kwargs):
            pass

    with pytest.raises(ValueError, match="Tool name must be a non-empty string."):
        InvalidNameTool(name="", description="valid description")

    with pytest.raises(ValueError, match="Tool description must be a non-empty string."):
        InvalidNameTool(name="valid_name", description="")

# ---------------------------------------------------------------------------
# 2. Calculator Tool Tests
# ---------------------------------------------------------------------------

def test_calculator_addition():
    calc = CalculatorTool()
    assert calc.execute("add", 10, 5) == 15
    assert calc.execute("+", 3, 7) == 10

def test_calculator_subtraction():
    calc = CalculatorTool()
    assert calc.execute("subtract", 20, 8) == 12
    assert calc.execute("-", 15, 5) == 10

def test_calculator_multiplication():
    calc = CalculatorTool()
    assert calc.execute("multiply", 6, 7) == 42
    assert calc.execute("*", 4, 3) == 12

def test_calculator_division():
    calc = CalculatorTool()
    assert calc.execute("divide", 20, 4) == 5.0
    assert calc.execute("/", 9, 3) == 3.0

def test_calculator_division_by_zero():
    calc = CalculatorTool()
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        calc.execute("divide", 10, 0)

def test_calculator_invalid_operation():
    calc = CalculatorTool()
    with pytest.raises(ValueError, match="Unsupported operation 'power'"):
        calc.execute("power", 2, 3)

# ---------------------------------------------------------------------------
# 3. Tool Registry Tests
# ---------------------------------------------------------------------------

def test_registry_register_and_get():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    retrieved = registry.get("dummy")
    assert retrieved is tool
    assert retrieved.name == "dummy"

def test_registry_list_tools():
    registry = ToolRegistry()
    registry.register(DummyTool())
    registry.register(CalculatorTool())

    tools = registry.list_tools()
    assert len(tools) == 2
    tool_names = [t["name"] for t in tools]
    assert "dummy" in tool_names
    assert "calculator" in tool_names

def test_registry_unknown_tool_lookup():
    registry = ToolRegistry()
    assert registry.get("nonexistent") is None
    assert registry.get_func("nonexistent") is None

def test_registry_invalid_registration():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Must provide a BaseTool instance."):
        registry.register("not_a_tool")  # type: ignore

# ---------------------------------------------------------------------------
# 4. End-to-End Integration Flow Test
# ---------------------------------------------------------------------------

def test_full_tool_system_integration_flow():
    # Step 1: Create CalculatorTool
    calculator = CalculatorTool()

    # Step 2: Register it in a clean ToolRegistry
    registry = ToolRegistry()
    registry.register(calculator)

    # Step 3: Retrieve "calculator" by name
    retrieved_tool = registry.get("calculator")
    assert retrieved_tool is not None

    # Step 4: Execute retrieved tool
    result = retrieved_tool.execute("multiply", 9, 9)

    # Step 5: Receive correct result
    assert result == 81
