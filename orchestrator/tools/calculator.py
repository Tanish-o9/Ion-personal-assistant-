from typing import Any, Union
from orchestrator.tools.interface import BaseTool
from orchestrator.tools.registry import ToolRegistry

Number = Union[int, float]

def calculate(operation: str, a: Number, b: Number) -> Number:
    """
    Performs basic arithmetic operations: addition, subtraction, multiplication, division.
    """
    op = operation.lower().strip()
    if op in ("add", "addition", "+"):
        return a + b
    elif op in ("subtract", "subtraction", "-"):
        return a - b
    elif op in ("multiply", "multiplication", "*"):
        return a * b
    elif op in ("divide", "division", "/"):
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
    else:
        raise ValueError(
            f"Unsupported operation '{operation}'. Supported operations: add, subtract, multiply, divide."
        )

class CalculatorTool(BaseTool):
    """
    JARVIS Calculator Tool implementing the BaseTool interface.
    """
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic arithmetic operations (addition, subtraction, multiplication, division).",
            metadata={"tier": 0},
            capabilities=["math", "arithmetic", "calculate", "calculator"],
            risk_level="low",
            latency_category="fast",
            cost_category="zero",
            cache_policy="LONG_TTL",
            requires_network=False,
            suitable_for_background=True,
            input_schema={"operation": "str", "a": "float", "b": "float"},
        )

    def execute(self, operation: str, a: Number, b: Number) -> Number:
        """
        Executes arithmetic calculation.
        """
        return calculate(operation, a, b)

def register_calculator(registry: ToolRegistry) -> None:
    """
    Registers an instance of CalculatorTool into a ToolRegistry instance.
    """
    calculator_tool = CalculatorTool()
    registry.register(calculator_tool)
