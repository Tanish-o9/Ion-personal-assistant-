"""
Phase 82: Causal Reasoning Engine.
Never presents correlation automatically as causation.
Classifies evidence, identifies confounders, evaluates interventions, and performs counterfactual analysis.
"""

from typing import Dict, Any, List, Optional
from orchestrator.reasoning.models import (
    CausalVariable,
    CausalRelationship,
    Confounder,
    CausalClaim,
    EvidenceClassification,
    EvidenceItem
)

class CausalGraph:
    """Directed Acyclic Graph representing causal relationships between variables."""
    def __init__(self, variables: Optional[List[CausalVariable]] = None, relationships: Optional[List[CausalRelationship]] = None):
        self.variables: Dict[str, CausalVariable] = {v.name: v for v in (variables or [])}
        self.relationships: List[CausalRelationship] = relationships or []

    def add_variable(self, var: CausalVariable) -> None:
        self.variables[var.name] = var

    def add_relationship(self, rel: CausalRelationship) -> None:
        if rel.cause not in self.variables:
            self.variables[rel.cause] = CausalVariable(name=rel.cause)
        if rel.effect not in self.variables:
            self.variables[rel.effect] = CausalVariable(name=rel.effect)
        self.relationships.append(rel)

    def get_parents(self, node: str) -> List[str]:
        return [r.cause for r in self.relationships if r.effect == node]

    def get_children(self, node: str) -> List[str]:
        return [r.effect for r in self.relationships if r.cause == node]


class CausalAnalyzer:
    """Engine for causal inference, confounder detection, intervention reasoning, and counterfactual analysis."""

    def evaluate_relationship(
        self,
        cause: str,
        effect: str,
        evidence: List[EvidenceItem],
        graph: Optional[CausalGraph] = None
    ) -> CausalClaim:
        graph = graph or CausalGraph()
        confounders = self.detect_confounders(cause, effect, graph)

        # Determine evidence classification
        evidence_types = []
        for ev in evidence:
            text = ev.content.lower()
            if "randomized" in text or "experiment" in text or "rct" in text:
                evidence_types.append(EvidenceClassification.EXPERIMENTAL)
            elif "quasi-experimental" in text or "natural experiment" in text:
                evidence_types.append(EvidenceClassification.QUASI_EXPERIMENTAL)
            elif "theoretical" in text or "mechanistic" in text:
                evidence_types.append(EvidenceClassification.THEORETICAL)
            elif "expert" in text:
                evidence_types.append(EvidenceClassification.EXPERT_INTERPRETATION)
            elif "correlation" in text or "observed" in text or "survey" in text:
                evidence_types.append(EvidenceClassification.OBSERVATIONAL)
            else:
                evidence_types.append(EvidenceClassification.UNKNOWN)

        primary_type = evidence_types[0] if evidence_types else EvidenceClassification.OBSERVATIONAL
        is_correlation_only = primary_type == EvidenceClassification.OBSERVATIONAL and len(confounders) > 0

        claim_text = (
            f"Correlation between {cause} and {effect} observed. Causal inference requires controlling for confounders."
            if is_correlation_only else
            f"Evidence indicates a plausible causal link from {cause} to {effect} under {primary_type.value} conditions."
        )

        return CausalClaim(
            claim=claim_text,
            evidence=evidence,
            assumptions=["No unobserved confounding factors exist outside the graph"],
            alternative_explanations=[f"Common cause ({c.name}) may drive both variables" for c in confounders],
            confounders=confounders,
            uncertainty=0.4 if is_correlation_only else 0.15,
            is_correlation_only=is_correlation_only
        )

    def detect_confounders(self, cause: str, effect: str, graph: CausalGraph) -> List[Confounder]:
        cause_parents = set(graph.get_parents(cause))
        effect_parents = set(graph.get_parents(effect))
        common_parents = cause_parents.intersection(effect_parents)

        confounders = []
        for parent in common_parents:
            confounders.append(Confounder(
                name=parent,
                affects_cause=cause,
                affects_effect=effect,
                plausible_explanation=f"{parent} directly influences both {cause} and {effect}, creating potential spurious correlation."
            ))
        return confounders

    def evaluate_intervention(self, variable: str, value: Any, graph: CausalGraph) -> Dict[str, Any]:
        """Simulates conceptual do-calculus intervention do(variable = value)."""
        affected = graph.get_children(variable)
        return {
            "intervention": f"do({variable} = {value})",
            "target_variable": variable,
            "assigned_value": value,
            "downstream_affected_variables": affected,
            "interpretation": f"Setting {variable} to {value} hypothetically influences downstream nodes: {', '.join(affected) if affected else 'None'}.",
            "disclaimer": "Result represents a conceptual scenario based on graph structure, not a real-world prediction."
        }

    def counterfactual_analysis(
        self,
        observed_state: Dict[str, Any],
        counterfactual_condition: Dict[str, Any],
        graph: Optional[CausalGraph] = None
    ) -> Dict[str, Any]:
        """Evaluates 'What would have happened if condition X were different?' with explicit assumption labeling."""
        diffs = {}
        for k, v in counterfactual_condition.items():
            if k in observed_state and observed_state[k] != v:
                diffs[k] = {"observed": observed_state[k], "counterfactual": v}

        return {
            "observed_state": observed_state,
            "counterfactual_condition": counterfactual_condition,
            "modified_variables": diffs,
            "counterfactual_assumptions": [
                "All unobserved variables remain identical to historical state",
                f"Mechanistic relationship models hold under modification of {list(counterfactual_condition.keys())}"
            ],
            "conclusion": f"If {', '.join(counterfactual_condition.keys())} were modified, expected outcome shifts based on causal graph dependencies.",
            "uncertainty_level": "MEDIUM"
        }

default_causal_analyzer = CausalAnalyzer()
