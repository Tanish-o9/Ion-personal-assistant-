import re
from typing import Optional, Dict, Any

from orchestrator.planning.models import TaskPlan, TaskStep, MAX_PLAN_STEPS
from orchestrator.planning.complexity import ComplexityAssessor
from orchestrator.planning.tool_selector import IntelligentToolSelector
from orchestrator.tools import parse_math_request, parse_web_request

class Planner:
    """
    Adaptive planner creating structured TaskPlans based on request complexity, tool metadata, and execution budgets.
    """
    def __init__(self, max_steps: int = MAX_PLAN_STEPS, tool_selector: Optional[IntelligentToolSelector] = None):
        self.max_steps = max_steps
        self.tool_selector = tool_selector or IntelligentToolSelector()

    def requires_planning(self, text: str) -> bool:
        """
        Returns True if request requires a multi-step plan, False for simple requests.
        """
        if not text:
            return False

        route = ComplexityAssessor.assess_route(text)
        return route in {"multi_step_task", "research_task", "knowledge_task"}

    def create_plan(self, request: str, has_files: bool = False, is_background: bool = False) -> TaskPlan:
        """
        Constructs an adaptive TaskPlan for a request.
        """
        route = ComplexityAssessor.assess_route(request, has_files=has_files, is_background=is_background)
        plan = TaskPlan(task_description=request, route=route, max_steps=self.max_steps)
        lowered = request.lower().strip()

        # Step 1: Check arithmetic request
        math_req = parse_math_request(request)
        if math_req:
            step1 = TaskStep(
                step_id=1,
                description=f"Calculate {math_req['a']} {math_req['operation']} {math_req['b']}",
                tool_name=math_req["tool_name"],
                arguments={
                    "operation": math_req["operation"],
                    "a": math_req["a"],
                    "b": math_req["b"],
                },
            )
            plan.add_step(step1)

            if "explain" in lowered:
                step2 = TaskStep(
                    step_id=2,
                    description="Explain the calculation result to the user",
                    tool_name=None,
                    depends_on=[1],
                )
                plan.add_step(step2)
            elif "greater than" in lowered or "compare" in lowered or "check if" in lowered:
                cmp_match = re.search(r"(?:greater than|less than|compare with|equal to)\s*(\d+)", lowered)
                cmp_val = cmp_match.group(1) if cmp_match else "50"
                step2 = TaskStep(
                    step_id=2,
                    description=f"Compare calculation result with {cmp_val}",
                    tool_name=None,
                    arguments={"compare_to": int(cmp_val) if cmp_val.isdigit() else 50},
                    depends_on=[1],
                )
                plan.add_step(step2)
            return plan

        # Step 2: Check web research request
        web_req = parse_web_request(request)
        if web_req or route == "research_task":
            t_name = web_req.get("tool_name", "web_search") if web_req else "web_search"
            t_args = {"query": web_req.get("query", request)} if web_req else {"query": request}

            step1 = TaskStep(
                step_id=1,
                description=f"Perform web research for: '{request}'",
                tool_name=t_name,
                arguments=t_args,
            )
            plan.add_step(step1)

            step2 = TaskStep(
                step_id=2,
                description="Synthesize research findings into a structured answer",
                tool_name=None,
                depends_on=[1],
            )
            plan.add_step(step2)
            return plan

        # Step 3: General multi-step text request fallback
        step1 = TaskStep(
            step_id=1,
            description=f"Analyze and process request: '{request}'",
            tool_name=None,
        )
        plan.add_step(step1)

        if "explain" in lowered or "summarize" in lowered:
            step2 = TaskStep(
                step_id=2,
                description="Format explanation and summary",
                tool_name=None,
                depends_on=[1],
            )
            plan.add_step(step2)

        return plan
