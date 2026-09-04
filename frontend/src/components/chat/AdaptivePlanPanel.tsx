import {
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineClock,
  HiOutlineRefresh,
  HiOutlineShieldCheck,
  HiOutlineLightningBolt,
} from 'react-icons/hi';
import { TaskPlan as TaskPlanData, TaskStepItem as TaskStepData } from '../../hooks/useWebSocket';

interface AdaptivePlanPanelProps {
  plan: TaskPlanData;
}

export default function AdaptivePlanPanel({ plan }: AdaptivePlanPanelProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <HiOutlineCheckCircle className="text-emerald-400 shrink-0" size={18} />;
      case 'failed':
        return <HiOutlineXCircle className="text-rose-400 shrink-0" size={18} />;
      case 'replanned':
        return <HiOutlineRefresh className="text-amber-400 shrink-0" size={18} />;
      default:
        return <HiOutlineClock className="text-slate-400 animate-spin shrink-0" size={18} />;
    }
  };

  const getRouteLabel = (route?: string) => {
    switch (route) {
      case 'research_task':
        return 'Web Research Task';
      case 'knowledge_task':
        return 'RAG Knowledge Task';
      case 'single_tool':
        return 'Fast Single Tool';
      case 'multimodal_task':
        return 'Multimodal Task';
      default:
        return 'Multi-Step Adaptive Task';
    }
  };

  const getConfidenceBadge = (confidence?: string) => {
    switch (confidence) {
      case 'high':
        return 'bg-emerald-500/10 text-emerald-300 ring-emerald-400/20';
      case 'medium':
        return 'bg-amber-500/10 text-amber-300 ring-amber-400/20';
      case 'low':
        return 'bg-rose-500/10 text-rose-300 ring-rose-400/20';
      default:
        return 'bg-slate-500/10 text-slate-300 ring-slate-400/20';
    }
  };

  return (
    <div className="my-3 rounded-2xl border border-white/10 bg-slate-900/80 p-4 backdrop-blur-xl shadow-futuristic font-sans text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 border-b border-white/5 pb-2.5">
        <div className="flex items-center gap-2">
          <HiOutlineLightningBolt size={16} className="text-brand-400" />
          <span className="font-semibold text-white uppercase tracking-wider">{getRouteLabel(plan.route)}</span>
        </div>

        <div className="flex items-center gap-2">
          {plan.replan_count && plan.replan_count > 0 ? (
            <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 font-mono text-[11px] text-amber-300 ring-1 ring-amber-400/30">
              Replans: {plan.replan_count}
            </span>
          ) : null}

          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 uppercase tracking-wider ${getConfidenceBadge(
              plan.confidence
            )}`}
          >
            <HiOutlineShieldCheck size={14} /> Confidence: {plan.confidence || 'Medium'}
          </span>
        </div>
      </div>

      <p className="text-slate-300 mb-3 italic">"{plan.task_description || plan.goal || 'Adaptive Execution Plan'}"</p>

      <div className="space-y-2">
        {plan.steps &&
          plan.steps.map((step: TaskStepData) => (
            <div
              key={step.step_id}
              className="flex items-start justify-between gap-3 rounded-xl bg-slate-950/70 p-3 border border-white/5"
            >
              <div className="flex items-start gap-2.5">
                {getStatusIcon(step.status)}
                <div>
                  <p className="font-medium text-slate-200">
                    Step {step.step_id}: {step.description}
                  </p>
                  {step.tool_name && (
                    <span className="mt-1 inline-block rounded-md bg-brand-500/10 px-2 py-0.5 font-mono text-[10px] text-brand-300">
                      Tool: {step.tool_name}
                    </span>
                  )}
                  {step.result && (
                    <p className="mt-1 text-slate-400 text-[11px] font-mono truncate max-w-md">
                      Result: {typeof step.result === 'object' ? JSON.stringify(step.result) : String(step.result)}
                    </p>
                  )}
                  {step.error && <p className="mt-1 text-rose-400 text-[11px] font-mono">Error: {step.error}</p>}
                </div>
              </div>

              <span className="capitalize font-mono text-[10px] text-slate-500">{step.status}</span>
            </div>
          ))}
      </div>
    </div>
  );
}
