import logging
import time
import re
from typing import Any, Dict, List, Optional
from orchestrator.tools.interface import BaseTool
from orchestrator.tools.registry import ToolRegistry
from orchestrator.observability import default_metrics, jarvis_logger

logger = logging.getLogger(__name__)

class ToolResult:
    """
    Structured representation of a tool execution result.
    """
    def __init__(
        self,
        tool_name: str,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
    ):
        self.tool_name = tool_name
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }

class ToolExecutor:
    """
    Generic tool executor responsible for looking up tools in a ToolRegistry
    and safely executing them with provided arguments.
    Instrumented with production latency metrics.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, *args: Any, **kwargs: Any) -> ToolResult:
        """
        Executes a registered tool by name with arguments.
        Returns a ToolResult object and handles errors cleanly.
        """
        start_time = time.time()
        tool = self.registry.get(tool_name)
        if not tool:
            duration_ms = (time.time() - start_time) * 1000
            default_metrics.record_tool(tool_name=tool_name, duration_ms=duration_ms, success=False)
            jarvis_logger.warning("Tool execution error: Tool '%s' is not registered.", tool_name)
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=f"Unknown tool: '{tool_name}' is not registered in ToolRegistry.",
            )

        try:
            output = tool.execute(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            default_metrics.record_tool(tool_name=tool_name, duration_ms=duration_ms, success=True)
            return ToolResult(
                tool_name=tool_name,
                success=True,
                output=output,
                error=None,
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            default_metrics.record_tool(tool_name=tool_name, duration_ms=duration_ms, success=False)
            jarvis_logger.warning("Tool '%s' execution failed: %s", tool_name, exc)
            return ToolResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=str(exc),
            )

def parse_math_request(text: str) -> Optional[Dict[str, Any]]:
    """
    Helper to detect and parse arithmetic requests from user text.
    Returns kwargs for CalculatorTool if matched, otherwise None.
    """
    lowered = text.lower().strip()
    normalized = (
        lowered.replace("multiplied by", "*")
        .replace("times", "*")
        .replace("divided by", "/")
        .replace("plus", "+")
        .replace("minus", "-")
    )

    pattern = r"(\b\d+(?:\.\d+)?\b)\s*([\+\-\*/])\s*(\b\d+(?:\.\d+)?\b)"
    match = re.search(pattern, normalized)
    if match:
        raw1, op_symbol, raw2 = match.groups()
        num1 = float(raw1) if "." in raw1 else int(raw1)
        num2 = float(raw2) if "." in raw2 else int(raw2)

        op_map = {"+": "add", "-": "subtract", "*": "multiply", "/": "divide"}
        return {
            "tool_name": "calculator",
            "operation": op_map.get(op_symbol, "add"),
            "a": num1,
            "b": num2,
        }
    return None

def parse_web_request(text: str) -> Optional[Dict[str, Any]]:
    """
    Helper to detect web_search or web_fetch requests from user text.
    """
    if not text:
        return None

    # Check for direct URL fetch requests
    url_match = re.search(r"https?://[^\s]+", text)
    if url_match and ("fetch" in text.lower() or "read" in text.lower() or "get" in text.lower()):
        return {
            "tool_name": "web_fetch",
            "url": url_match.group(0),
        }

    # Check for search requests
    lowered = text.lower().strip()
    search_keywords = ["search for", "research", "look up", "find info on", "what is "]
    for kw in search_keywords:
        if kw in lowered:
            query = text[lowered.find(kw) + len(kw):].strip()
            if query:
                return {
                    "tool_name": "web_search",
                    "query": query,
                }

    return None
