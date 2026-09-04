import { HiOutlineTerminal } from 'react-icons/hi';
import { ToolExecution } from '../../hooks/useWebSocket';

interface ToolExecutionPanelProps {
  tools: ToolExecution[];
}

export default function ToolExecutionPanel({ tools }: ToolExecutionPanelProps) {
  if (!tools || tools.length === 0) return null;

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex items-center gap-3 mb-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-400/20">
          <HiOutlineTerminal size={20} />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Tool System</p>
          <h3 className="text-lg font-semibold text-white">Executed Tools</h3>
        </div>
      </div>

      <div className="space-y-3">
        {tools.map((t, idx) => (
          <div key={idx} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs font-mono">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="font-semibold text-cyan-300">Tool: {t.tool_name}</span>
              <span className={t.success !== false ? 'text-emerald-400' : 'text-rose-400'}>
                {t.result !== undefined ? (t.success !== false ? 'Status: Completed' : 'Status: Failed') : 'Status: Executing...'}
              </span>
            </div>
            <div className="text-slate-300">
              <span className="text-slate-500">Input: </span>
              {JSON.stringify(t.args)}
            </div>
            {t.result !== undefined && (
              <div className="mt-2 text-slate-200 border-t border-slate-800 pt-2">
                <span className="text-slate-500">Result: </span>
                {typeof t.result === 'object' ? JSON.stringify(t.result) : String(t.result)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
