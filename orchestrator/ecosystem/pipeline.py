from typing import Tuple
from orchestrator.ecosystem.models import EcosystemCatalogEntry

class CapabilityValidationPipeline:
    """
    Validation pipeline enforcing manifest structure, security checks, and evaluation approvals
    before publishing capabilities into the ecosystem catalog.
    """
    @staticmethod
    def validate_and_approve(entry: EcosystemCatalogEntry) -> Tuple[bool, str]:
        if not entry.name or not entry.version:
            return False, "Validation failed: missing name or version."

        if "credentials_harvesting" in entry.required_permissions or "unrestricted_shell" in entry.required_permissions:
            entry.evaluation_status = "rejected"
            return False, "Security check failed: dangerous permissions requested."

        entry.evaluation_status = "passed"
        return True, "Validation and evaluation passed."
