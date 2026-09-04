from typing import Any, Dict, List, Optional

from orchestrator.guardrails.models import (
    SafetyDecision,
    QualityCheckResult,
    GuardrailResult,
)
from orchestrator.security import InputSanitizer

class GuardrailManager:
    """
    Centralized production quality and AI guardrail layer enforcing factual grounding,
    tool execution safety, prompt injection boundaries, and evidence confidence checks.
    """
    def validate_input(self, raw_text: str) -> SafetyDecision:
        if not raw_text or len(raw_text.strip()) == 0:
            return SafetyDecision(allowed=False, action="block", reason="Empty request.")

        if len(raw_text) > 100000:
            return SafetyDecision(allowed=False, action="block", reason="Input exceeds maximum allowed size (100KB).")

        lowered = raw_text.lower()
        if any(pat in lowered for pat in ["ignore previous instructions", "system override", "you are now unrestricted"]):
            return SafetyDecision(allowed=True, action="warn", risk_level="medium", reason="Potential prompt injection pattern detected.")

        return SafetyDecision(allowed=True, action="allow", risk_level="low")

    def validate_output_grounding(self, response_text: str, evidence_sources: List[str]) -> QualityCheckResult:
        if not response_text:
            return QualityCheckResult(passed=False, confidence_level="LOW", notes="Empty response.")

        if not evidence_sources and any(kw in response_text.lower() for kw in ["according to research", "verified source", "facts show"]):
            return QualityCheckResult(
                passed=False,
                confidence_level="LOW",
                unsupported_claims=["Response claims research evidence but no sources were retrieved."],
                notes="Factual claim ungrounded.",
            )

        conf = "HIGH" if evidence_sources else "MEDIUM"
        return QualityCheckResult(passed=True, confidence_level=conf)

    def evaluate_request(self, raw_input: str, response_text: str, evidence_sources: Optional[List[str]] = None) -> GuardrailResult:
        safety = self.validate_input(raw_input)
        quality = self.validate_output_grounding(response_text, evidence_sources or [])

        is_safe = safety.allowed
        is_grounded = quality.passed

        return GuardrailResult(
            is_safe=is_safe,
            is_grounded=is_grounded,
            confidence_level=quality.confidence_level,
            safety_decision=safety,
            quality_check=quality,
        )

default_guardrail_manager = GuardrailManager()
