import logging
from typing import Any, Dict, Optional
from orchestrator.planning.models import TaskPlan, TaskStep
from orchestrator.planning.tool_selector import IntelligentToolSelector
from orchestrator.planning.verifier import AdaptiveVerifier
from orchestrator.tools import ToolExecutor, default_executor
from orchestrator.observability import jarvis_logger, default_metrics

logger = logging.getLogger(__name__)

def classify_failure(error_msg: str) -> str:
    """
    Classifies step failure into a deterministic failure category.
    """
    if not error_msg:
        return "non_retryable"

    lowered = error_msg.lower()
    if "time" in lowered or "timeout" in lowered:
        return "timeout"
    elif "connect" in lowered or "http" in lowered or "network" in lowered:
        return "external_service_failure"
    elif "unknown tool" in lowered or "not registered" in lowered:
        return "tool_unavailable"
    elif "argument" in lowered or "valueerror" in lowered or "invalid" in lowered:
        return "invalid_input"
    elif "blocked" in lowered or "access denied" in lowered:
        return "authorization_failure"
    elif "no results" in lowered or "empty" in lowered:
        return "insufficient_evidence"
    
    return "retryable"

class TaskExecutor:
    """
    Executes each step of an adaptive TaskPlan sequentially with bounded retries, failure classification, and step replanning.
    """
    def __init__(
        self,
        tool_executor: Optional[ToolExecutor] = None,
        tool_selector: Optional[IntelligentToolSelector] = None,
    ):
        self.tool_executor = tool_executor or default_executor
        self.tool_selector = tool_selector or IntelligentToolSelector()

    def execute_plan(self, plan: TaskPlan, user_id: str = "default_user") -> TaskPlan:
        """
        Executes an adaptive TaskPlan with bounded retries and step self-correction.
        """
        plan.status = "running"
        previous_result: Any = None
        tool_rounds = 0

        for step in plan.steps:
            if tool_rounds >= plan.max_tool_rounds:
                plan.status = "failed"
                logger.warning("TaskPlan budget exhausted: max tool rounds (%d) reached.", plan.max_tool_rounds)
                break

            step.status = "running"

            if step.tool_name:
                tool_rounds += 1
                is_valid, err = self.tool_selector.validate_tool_execution(step.tool_name, step.arguments, user_id=user_id)
                if not is_valid:
                    step.status = "failed"
                    step.error = err
                    step.failure_category = "authorization_failure"
                    plan.status = "failed"
                    break

                # Execute tool step with bounded retries (max 2 retries)
                max_retries = 2
                success = False

                for attempt in range(max_retries + 1):
                    tool_res = self.tool_executor.execute(step.tool_name, **step.arguments)
                    if tool_res.success:
                        step.status = "completed"
                        step.result = tool_res.output
                        previous_result = tool_res.output
                        success = True
                        break
                    else:
                        step.retry_count += 1
                        step.error = tool_res.error
                        step.failure_category = classify_failure(tool_res.error or "")

                        if step.failure_category not in {"retryable", "timeout", "external_service_failure"}:
                            break

                if not success:
                    # Attempt step replan if replan budget allows
                    if plan.replan_count < plan.max_replans and step.failure_category in {"tool_unavailable", "invalid_input"}:
                        alt_tool = self.tool_selector.select_tool_for_step(step.description)
                        if alt_tool and alt_tool.name != step.tool_name:
                            plan.replan_count += 1
                            step.tool_name = alt_tool.name
                            step.status = "replanned"
                            jarvis_logger.info("Replanned step %d with alternative tool '%s'", step.step_id, alt_tool.name)

                            alt_res = self.tool_executor.execute(alt_tool.name, **step.arguments)
                            if alt_res.success:
                                step.status = "completed"
                                step.result = alt_res.output
                                previous_result = alt_res.output
                                success = True

                    if not success:
                        step.status = "failed"
                        plan.status = "failed"
                        logger.warning("TaskPlan failed at step %d: %s", step.step_id, step.error)
                        break
            else:
                # Non-tool step
                try:
                    if "compare" in step.description.lower() and previous_result is not None:
                        cmp_val = step.arguments.get("compare_to", 50)
                        is_greater = previous_result > cmp_val
                        step.result = f"{previous_result} is {'greater' if is_greater else 'not greater'} than {cmp_val}"
                    else:
                        step.result = f"Processed step {step.step_id} using previous result: {previous_result}"
                    step.status = "completed"
                except Exception as exc:
                    step.status = "failed"
                    step.error = str(exc)
                    step.failure_category = "non_retryable"
                    plan.status = "failed"
                    break

        if all(s.status in {"completed", "replanned"} for s in plan.steps):
            plan.status = "completed"

        # Adaptive verification & confidence assessment
        AdaptiveVerifier.verify_plan(plan)
        return plan

class Verifier:
    """
    Deterministic verifier for TaskPlans (Backward compatibility wrapper around AdaptiveVerifier).
    """
    @staticmethod
    def verify(plan: TaskPlan) -> Dict[str, Any]:
        return AdaptiveVerifier.verify_plan(plan)
