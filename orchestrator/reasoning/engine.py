"""
Phase 56: Advanced Reasoning Engine & Evidence Analysis.
"""

from typing import Dict, Any, List, Optional
from orchestrator.reasoning.models import ReasoningStrategy, ReasoningContext, EvidenceItem

class AdvancedReasoningEngine:
    """Provides evidence-based reasoning, strategy selection, conflict detection, and verification."""

    def select_strategy(self, context: ReasoningContext) -> ReasoningStrategy:
        task_lower = context.task.lower()

        if context.current_iteration >= context.max_reasoning_iterations:
            return ReasoningStrategy.ASK_USER

        if "compare" in task_lower or "versus" in task_lower:
            return ReasoningStrategy.COMPARE

        if "verify" in task_lower or "check" in task_lower:
            return ReasoningStrategy.VERIFY

        if "research" in task_lower or "find info" in task_lower:
            return ReasoningStrategy.RESEARCH

        if len(task_lower.split()) > 15 or "build" in task_lower or "develop" in task_lower:
            return ReasoningStrategy.DECOMPOSE

        return ReasoningStrategy.DIRECT

    def analyze_evidence(self, context: ReasoningContext) -> Dict[str, Any]:
        """Detects conflicts or uncertainty across gathered evidence."""
        if not context.evidence:
            context.uncertainty = 0.8
            context.verification_status = "UNCERTAIN"
            return {"status": "UNCERTAIN", "conflicts": [], "confidence": 0.2}

        conflicts = []
        contents = [e.content.lower() for e in context.evidence]

        # Basic conflict check heuristic across evidence sources
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                c1, c2 = contents[i], contents[j]
                if ("not " in c1 and c1.replace("not ", "").strip() in c2) or ("not " in c2 and c2.replace("not ", "").strip() in c1):
                    conflicts.append((context.evidence[i].source, context.evidence[j].source))


        if conflicts:
            context.uncertainty = 0.9
            context.verification_status = "CONFLICTING"
            return {"status": "CONFLICTING", "conflicts": conflicts, "confidence": 0.1}

        avg_confidence = sum(e.confidence for e in context.evidence) / len(context.evidence)
        context.uncertainty = round(1.0 - avg_confidence, 2)
        context.verification_status = "VERIFIED" if avg_confidence > 0.7 else "UNCERTAIN"

        return {
            "status": context.verification_status,
            "conflicts": [],
            "confidence": round(avg_confidence, 2)
        }

default_reasoning_engine = AdvancedReasoningEngine()
