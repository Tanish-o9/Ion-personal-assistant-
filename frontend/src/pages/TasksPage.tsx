import TaskPanel from '../components/task/TaskPanel';
import ToolExecutionPanel from '../components/tools/ToolExecutionPanel';
import { useWebSocket } from '../hooks/useWebSocket';

interface TasksPageProps {
  sessionId: string;
  userId: string;
}

export default function TasksPage({ sessionId, userId }: TasksPageProps) {
  const { taskPlan, toolExecutions } = useWebSocket(sessionId, userId);

  return (
    <div className="space-y-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic">
        <h2 className="text-2xl font-semibold text-white">Execution Engine & Planning</h2>
        <p className="mt-1 text-xs text-slate-400">
          Visualizes multi-step planning tasks, tool executions, and step verification results.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <TaskPanel plan={taskPlan} />
        <ToolExecutionPanel tools={toolExecutions} />
      </div>
    </div>
  );
}
