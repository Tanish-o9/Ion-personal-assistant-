import { HiOutlineCheckCircle, HiOutlineClock, HiOutlineXCircle } from 'react-icons/hi';
import { TaskPlan } from '../../hooks/useWebSocket';

interface TaskPanelProps {
  plan: TaskPlan | null;
}

export default function TaskPanel({ plan }: TaskPanelProps) {
  if (!plan || !plan.steps || plan.steps.length === 0) return null;

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Execution Engine</p>
        <h3 className="text-lg font-semibold text-white">Task Plan ({plan.steps.length} Steps)</h3>
        {plan.goal && <p className="mt-1 text-xs text-slate-300">Goal: {plan.goal}</p>}
      </div>

      <div className="space-y-3">
        {plan.steps.map((step) => {
          const isDone = step.status === 'completed';
          const isFailed = step.status === 'failed';
          const isInProgress = step.status === 'in_progress';

          return (
            <div
              key={step.step_id}
              className={`flex items-start gap-3 rounded-2xl border p-4 text-xs transition ${
                isDone
                  ? 'border-emerald-500/20 bg-emerald-950/10 text-emerald-200'
                  : isFailed
                  ? 'border-rose-500/20 bg-rose-950/10 text-rose-200'
                  : isInProgress
                  ? 'border-brand-500/30 bg-brand-950/20 text-brand-200 ring-1 ring-brand-500/20'
                  : 'border-slate-800 bg-slate-950/60 text-slate-400'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isDone ? (
                  <HiOutlineCheckCircle size={18} className="text-emerald-400" />
                ) : isFailed ? (
                  <HiOutlineXCircle size={18} className="text-rose-400" />
                ) : (
                  <HiOutlineClock size={18} className="text-slate-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-white">Step {step.step_id}: {step.description}</span>
                  <span className="uppercase tracking-wider text-[10px] opacity-75">{step.status}</span>
                </div>
                {step.tool_name && (
                  <p className="mt-1 text-[11px] opacity-70">Tool: {step.tool_name}</p>
                )}
                {step.result && (
                  <p className="mt-1 rounded-lg bg-slate-900/80 p-2 font-mono text-[11px] text-slate-300">
                    {step.result}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
