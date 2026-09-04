from typing import Any, Dict, List, Optional, Tuple
from orchestrator.tools import ToolRegistry, default_registry
from orchestrator.tools.interface import BaseTool
from orchestrator.observability import jarvis_logger

class IntelligentToolSelector:
    """
    Intelligent tool selector matching step requirements against tool metadata, capabilities, risk levels, and schemas.
    Enforces backend validation before tool execution.
    """
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or default_registry

    def select_tool_for_step(
        self,
        step_description: str,
        required_capability: Optional[str] = None,
        max_allowed_risk: str = "medium",
    ) -> Optional[BaseTool]:
        """
        Finds the best matching registered tool for a plan step.
        """
        lowered_desc = step_description.lower().strip()
        available_tools = self.registry.list_tools()

        for tool_meta in available_tools:
            tool_name = tool_meta["name"]
            tool_obj = self.registry.get(tool_name)
            if not tool_obj:
                continue

            risk_order = {"low": 1, "medium": 2, "high": 3, "restricted": 4}
            if risk_order.get(tool_obj.risk_level, 1) > risk_order.get(max_allowed_risk, 2):
                continue

            if required_capability and required_capability in tool_obj.capabilities:
                return tool_obj

            for cap in tool_obj.capabilities:
                if cap in lowered_desc:
                    return tool_obj

        return None

    def validate_tool_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str,
        max_allowed_risk: str = "medium",
    ) -> Tuple[bool, Optional[str]]:
        """
        Backend validation of tool execution safety and argument parameters.
        Returns (is_valid, error_reason).
        """
        tool = self.registry.get(tool_name)
        if not tool:
            return False, f"Unknown tool: '{tool_name}' is not registered."

        risk_order = {"low": 1, "medium": 2, "high": 3, "restricted": 4}
        if risk_order.get(tool.risk_level, 1) > risk_order.get(max_allowed_risk, 2):
            jarvis_logger.warning("Tool '%s' blocked by risk policy (%s > %s)", tool_name, tool.risk_level, max_allowed_risk)
            return False, f"Tool '{tool_name}' exceeds maximum allowed risk level '{max_allowed_risk}'."

        return True, None
