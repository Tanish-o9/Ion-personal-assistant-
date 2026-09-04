from typing import Any, Dict, Optional

class ApprovalPolicyEvaluator:
    """
    Evaluates action risk levels and determines whether explicit human-in-the-loop approval is required.
    """
    @staticmethod
    def requires_approval(
        action_type: str,
        risk_level: str = "low",
        requires_confirmation: bool = False,
    ) -> bool:
        if requires_confirmation:
            return True

        risk_lower = risk_level.lower().strip()
        if risk_lower in {"high", "restricted", "blocked"}:
            return True

        # Specific action rules
        consequential_actions = ["system_delete", "database_drop", "network_modify", "grant_access"]
        if any(act in action_type.lower() for act in consequential_actions):
            return True

        return False
