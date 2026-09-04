from typing import Any, Callable, Dict, List, Optional
from orchestrator.tools.interface import BaseTool

class ToolRegistry:
    """
    Lightweight ToolRegistry to register, retrieve, and list BaseTool instances by name.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Registers a tool instance implementing BaseTool.
        """
        if not isinstance(tool, BaseTool):
            raise ValueError("Must provide a BaseTool instance.")
        if not tool.name:
            raise ValueError("Tool name must be a non-empty string.")

        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """
        Retrieves a registered BaseTool instance by name, or None if not found.
        """
        return self._tools.get(name)

    def get_func(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Retrieves the execute method of a tool by name, or None if not found.
        """
        tool = self._tools.get(name)
        return tool.execute if tool else None

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all registered tool metadata dictionaries.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "metadata": tool.metadata,
            }
            for tool in self._tools.values()
        ]
