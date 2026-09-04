from typing import List, Tuple

class ComputerAllowlist:
    """
    Configurable allowlist enforcement for local applications and target domains.
    """
    def __init__(self):
        self.allowed_applications = {"browser", "editor", "calculator", "terminal_read_only", "jarvis_dashboard"}
        self.allowed_domains = {"github.com", "python.org", "docs.python.org", "wikipedia.org"}
        self.blocked_keywords = {"password", "credential", "private_key", "secret", "payment", "bank"}

    def evaluate_action(self, application: str, target: str, action_type: str) -> Tuple[str, bool]:
        app_lower = application.lower().strip()
        target_lower = target.lower().strip()

        if any(kw in target_lower or kw in action_type.lower() for kw in self.blocked_keywords):
            return "blocked", False

        if app_lower not in self.allowed_applications:
            return "high", True  # High risk, requires confirmation

        if action_type in {"read_screen", "inspect_state"}:
            return "low", False

        if action_type in {"click_element", "scroll"}:
            return "medium", False

        if action_type in {"type_text", "submit_form"}:
            return "medium", True

        return "high", True

default_computer_allowlist = ComputerAllowlist()
