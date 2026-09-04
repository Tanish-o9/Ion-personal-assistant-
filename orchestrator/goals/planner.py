"""
Phase 55: Goal Decomposition Planner.
"""

from typing import List
from orchestrator.goals.models import GoalTaskStep, GoalTask, GoalMilestone

class GoalDecompositionPlanner:
    """Decomposes high-level objectives into sequential steps and hierarchical milestones for bounded multi-agent execution."""
    @staticmethod
    def decompose_goal(description: str) -> List[GoalTaskStep]:
        desc_lower = description.lower()

        steps: List[GoalTaskStep] = []
        step_num = 1

        # Step 1: Research & Discovery
        steps.append(GoalTaskStep(
            step_number=step_num,
            title=f"Research requirements for: {description[:40]}...",
            agent_type="research",
            tool_name="web_search"
        ))
        step_num += 1

        # Step 2: Implementation / Execution
        if "code" in desc_lower or "build" in desc_lower or "develop" in desc_lower:
            steps.append(GoalTaskStep(
                step_number=step_num,
                title="Execute code generation or file writing",
                agent_type="coding",
                tool_name="file_writer"
            ))
            step_num += 1
        elif "report" in desc_lower or "document" in desc_lower:
            steps.append(GoalTaskStep(
                step_number=step_num,
                title="Synthesize findings and generate document",
                agent_type="documents",
                tool_name="document_generator"
            ))
            step_num += 1
        else:
            steps.append(GoalTaskStep(
                step_number=step_num,
                title="Process task execution",
                agent_type="general",
                tool_name="task_executor"
            ))
            step_num += 1

        # Step 3: Verification & Quality Control
        steps.append(GoalTaskStep(
            step_number=step_num,
            title="Verify evidence and validate success criteria",
            agent_type="verification",
            tool_name="verifier"
        ))

        return steps

    @staticmethod
    def decompose_goal_hierarchical(description: str) -> List[GoalMilestone]:
        steps = GoalDecompositionPlanner.decompose_goal(description)
        
        # Milestone 1: Analysis & Discovery
        t1 = GoalTask(
            id="t1",
            title=steps[0].title,
            dependencies=[],
            steps=[steps[0]],
            status="PENDING",
            can_parallel=False
        )
        m1 = GoalMilestone(
            id="m1",
            title="Milestone 1: Discovery & Analysis",
            tasks=[t1],
            status="PENDING",
            expected_outcome="Requirements analyzed and discovery completed"
        )

        # Milestone 2: Core Execution (supports parallel independent tasks if multiple exist)
        t2 = GoalTask(
            id="t2",
            title=steps[1].title if len(steps) > 1 else "Execution",
            dependencies=["t1"],
            steps=[steps[1]] if len(steps) > 1 else [],
            status="PENDING",
            can_parallel=True
        )
        m2 = GoalMilestone(
            id="m2",
            title="Milestone 2: Execution & Synthesis",
            tasks=[t2],
            status="PENDING",
            expected_outcome="Primary deliverables generated"
        )

        # Milestone 3: Final Verification
        t3 = GoalTask(
            id="t3",
            title=steps[2].title if len(steps) > 2 else "Validation",
            dependencies=["t2"],
            steps=[steps[2]] if len(steps) > 2 else [],
            status="PENDING",
            can_parallel=False
        )
        m3 = GoalMilestone(
            id="m3",
            title="Milestone 3: Verification & Quality Control",
            tasks=[t3],
            status="PENDING",
            expected_outcome="Final output verified against success criteria"
        )

        return [m1, m2, m3]

