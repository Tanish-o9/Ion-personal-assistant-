from orchestrator.tools.interface import BaseTool
from orchestrator.tools.registry import ToolRegistry
from orchestrator.tools.calculator import calculate, CalculatorTool, register_calculator
from orchestrator.tools.executor import ToolExecutor, ToolResult, parse_math_request, parse_web_request
from orchestrator.tools.web import WebSearchTool, WebFetchTool

def get_default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    register_calculator(reg)
    reg.register(WebSearchTool())
    reg.register(WebFetchTool())
    try:
        from orchestrator.knowledge.retriever import KnowledgeSearchTool
        reg.register(KnowledgeSearchTool())
    except ImportError:
        pass
    return reg

default_registry = get_default_registry()
default_executor = ToolExecutor(default_registry)

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "CalculatorTool",
    "calculate",
    "register_calculator",
    "WebSearchTool",
    "WebFetchTool",
    "default_registry",
    "ToolExecutor",
    "ToolResult",
    "parse_math_request",
    "parse_web_request",
    "default_executor",
]
