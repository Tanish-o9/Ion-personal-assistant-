from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseTool(ABC):
    """
    Abstract Base Class for all JARVIS tools.

    Every tool must define a unique `name`, a short `description`,
    and an `execute(*args, **kwargs)` method.
    Extended in Phase 20 with rich metadata for intelligent tool selection.
    """
    def __init__(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None,
        risk_level: str = "low",               # low, medium, high, restricted
        latency_category: str = "fast",         # fast, medium, slow
        cost_category: str = "zero",            # zero, low, medium, high
        cache_policy: str = "NO_CACHE",         # NO_CACHE, SHORT_TTL, LONG_TTL
        requires_network: bool = False,
        suitable_for_background: bool = True,
        input_schema: Optional[Dict[str, Any]] = None,
    ):
        if not name or not isinstance(name, str):
            raise ValueError("Tool name must be a non-empty string.")
        if not description or not isinstance(description, str):
            raise ValueError("Tool description must be a non-empty string.")

        self.name = name
        self.description = description
        self.metadata = metadata if metadata is not None else {}

        # Phase 20 Extended Metadata Properties
        self.capabilities = capabilities or [name]
        self.risk_level = risk_level
        self.latency_category = latency_category
        self.cost_category = cost_category
        self.cache_policy = cache_policy
        self.requires_network = requires_network
        self.suitable_for_background = suitable_for_background
        self.input_schema = input_schema or {}

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the tool's core logic.
        """
        pass
