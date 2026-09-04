from typing import Any, Dict, List, Optional

VALID_STEP_STATUSES = {"pending", "running", "completed", "failed", "replanned"}
MAX_PLAN_STEPS = 8
MAX_TOOL_ROUNDS = 10
MAX_REPLANS = 2

class TaskStep:
    """
    Represents a single step in a multi-step TaskPlan.
    Extended in Phase 20 with failure classification and retry tracking.
    """
    def __init__(
        self,
        step_id: int,
        description: str,
        tool_name: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None,
        status: str = "pending",
        result: Optional[Any] = None,
        error: Optional[str] = None,
        retry_count: int = 0,
        failure_category: Optional[str] = None,
        depends_on: Optional[List[int]] = None,
    ):
        self.step_id = step_id
        self.description = description
        self.tool_name = tool_name
        self.arguments = arguments or {}
        self.status = status if status in VALID_STEP_STATUSES else "pending"
        self.result = result
        self.error = error
        self.retry_count = retry_count
        self.failure_category = failure_category
        self.depends_on = depends_on or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "failure_category": self.failure_category,
            "depends_on": self.depends_on,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskStep":
        return cls(
            step_id=data.get("step_id", 1),
            description=data.get("description", ""),
            tool_name=data.get("tool_name"),
            arguments=data.get("arguments"),
            status=data.get("status", "pending"),
            result=data.get("result"),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
            failure_category=data.get("failure_category"),
            depends_on=data.get("depends_on", []),
        )

class TaskPlan:
    """
    Represents an adaptive execution plan containing ordered steps to achieve a task.
    Extended in Phase 20 with route assessment, verification status, confidence, decision trace, and execution budgets.
    """
    def __init__(
        self,
        task_description: str,
        steps: Optional[List[TaskStep]] = None,
        status: str = "pending",
        route: str = "multi_step_task",
        max_steps: int = MAX_PLAN_STEPS,
        max_tool_rounds: int = MAX_TOOL_ROUNDS,
        max_replans: int = MAX_REPLANS,
        retry_count: int = 0,
        replan_count: int = 0,
        verification_status: str = "pending", # pending, passed, failed
        confidence: str = "medium",             # high, medium, low
        decision_trace: Optional[Dict[str, Any]] = None,
    ):
        self.task_description = task_description
        self.steps = (steps or [])[:max_steps]
        self.status = status if status in VALID_STEP_STATUSES else "pending"
        self.route = route
        self.max_steps = max_steps
        self.max_tool_rounds = max_tool_rounds
        self.max_replans = max_replans
        self.retry_count = retry_count
        self.replan_count = replan_count
        self.verification_status = verification_status
        self.confidence = confidence
        self.decision_trace = decision_trace or {
            "route": route,
            "steps_count": len(self.steps),
            "replans": replan_count,
            "verification": verification_status,
            "confidence": confidence,
        }

    def add_step(self, step: TaskStep) -> bool:
        if len(self.steps) < self.max_steps:
            self.steps.append(step)
            self.decision_trace["steps_count"] = len(self.steps)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_description": self.task_description,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "route": self.route,
            "max_steps": self.max_steps,
            "max_tool_rounds": self.max_tool_rounds,
            "max_replans": self.max_replans,
            "retry_count": self.retry_count,
            "replan_count": self.replan_count,
            "verification_status": self.verification_status,
            "confidence": self.confidence,
            "decision_trace": self.decision_trace,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskPlan":
        steps_data = data.get("steps", [])
        steps = [TaskStep.from_dict(s) for s in steps_data]
        return cls(
            task_description=data.get("task_description", ""),
            steps=steps,
            status=data.get("status", "pending"),
            route=data.get("route", "multi_step_task"),
            max_steps=data.get("max_steps", MAX_PLAN_STEPS),
            max_tool_rounds=data.get("max_tool_rounds", MAX_TOOL_ROUNDS),
            max_replans=data.get("max_replans", MAX_REPLANS),
            retry_count=data.get("retry_count", 0),
            replan_count=data.get("replan_count", 0),
            verification_status=data.get("verification_status", "pending"),
            confidence=data.get("confidence", "medium"),
            decision_trace=data.get("decision_trace"),
        )
