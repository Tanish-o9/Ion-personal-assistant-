import { useState, useEffect } from 'react';
import {
  HiOutlineHeart,
  HiOutlineChip,
  HiOutlineTerminal,
  HiOutlineCog,
  HiOutlineChatAlt2,
  HiOutlineClock,
  HiOutlineExclamationCircle,
} from 'react-icons/hi';
import { api } from '../../services/api';

export interface MonitoringData {
  service: string;
  metrics: {
    requests: { total_requests: number; total_errors: number };
    llm: { total_requests: number; failures: number; fallbacks: number; avg_latency_ms: number };
    tools: { total_calls: number; failures: number; by_tool: Record<string, number> };
    jobs: { created: number; completed: number; failed: number; cancelled: number };
    websocket: { active_connections: number; messages_received: number; messages_sent: number; errors: number };
  };
}

export default function DeveloperPanel() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [readyStatus, setReadyStatus] = useState<string>('Checking...');

  const loadMonitoringData = async () => {
    try {
      const resSummary = await api.get('/monitoring/summary');
      setData(resSummary.data);

      const resReady = await api.get('/ready');
      setReadyStatus(resReady.data.status === 'ready' ? 'Ready' : 'Degraded');
    } catch (err) {
      console.error('Failed to fetch monitoring summary:', err);
      setReadyStatus('Unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMonitoringData();
    const interval = setInterval(loadMonitoringData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center rounded-[2rem] border border-white/10 bg-slate-900/70 p-8 text-xs font-mono text-slate-400">
        Loading system telemetry...
      </div>
    );
  }

  const m = data?.metrics;

  return (
    <div className="space-y-6 font-sans">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Developer Telemetry</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">System Observability Dashboard</h2>
            <p className="mt-1 text-xs text-slate-400 font-mono">Service: {data?.service || 'JARVIS Orchestrator'}</p>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${
                readyStatus === 'Ready'
                  ? 'bg-emerald-500/10 text-emerald-300 ring-emerald-400/20'
                  : 'bg-rose-500/10 text-rose-300 ring-rose-400/20'
              }`}
            >
              <HiOutlineHeart size={16} /> System {readyStatus}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs uppercase tracking-wider font-medium">HTTP Requests</span>
            <HiOutlineClock size={20} className="text-brand-400" />
          </div>
          <p className="text-2xl font-bold text-white">{m?.requests.total_requests || 0}</p>
          <p className="mt-1 text-xs text-slate-400">Errors: {m?.requests.total_errors || 0}</p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs uppercase tracking-wider font-medium">LLM Performance</span>
            <HiOutlineChip size={20} className="text-brand-400" />
          </div>
          <p className="text-2xl font-bold text-white">{m?.llm.total_requests || 0} calls</p>
          <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
            <span>Avg: {m?.llm.avg_latency_ms || 0}ms</span>
            <span className="text-amber-400 font-medium">Fallbacks: {m?.llm.fallbacks || 0}</span>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs uppercase tracking-wider font-medium">Tool Executions</span>
            <HiOutlineTerminal size={20} className="text-brand-400" />
          </div>
          <p className="text-2xl font-bold text-white">{m?.tools.total_calls || 0} calls</p>
          <p className="mt-1 text-xs text-slate-400">Failures: {m?.tools.failures || 0}</p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 backdrop-blur-xl">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs uppercase tracking-wider font-medium">WebSockets</span>
            <HiOutlineChatAlt2 size={20} className="text-brand-400" />
          </div>
          <p className="text-2xl font-bold text-white">{m?.websocket.active_connections || 0} active</p>
          <p className="mt-1 text-xs text-slate-400">Sent: {m?.websocket.messages_sent || 0} | Recv: {m?.websocket.messages_received || 0}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineCog size={20} className="text-brand-400" />
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Background Job Metrics</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-2xl bg-slate-950/70 p-4 border border-white/5">
              <span className="text-xs text-slate-400">Created</span>
              <p className="text-xl font-bold text-white mt-1">{m?.jobs.created || 0}</p>
            </div>
            <div className="rounded-2xl bg-slate-950/70 p-4 border border-white/5">
              <span className="text-xs text-emerald-400">Completed</span>
              <p className="text-xl font-bold text-emerald-300 mt-1">{m?.jobs.completed || 0}</p>
            </div>
            <div className="rounded-2xl bg-slate-950/70 p-4 border border-white/5">
              <span className="text-xs text-rose-400">Failed</span>
              <p className="text-xl font-bold text-rose-300 mt-1">{m?.jobs.failed || 0}</p>
            </div>
            <div className="rounded-2xl bg-slate-950/70 p-4 border border-white/5">
              <span className="text-xs text-amber-400">Cancelled</span>
              <p className="text-xl font-bold text-amber-300 mt-1">{m?.jobs.cancelled || 0}</p>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-4">
            <HiOutlineExclamationCircle size={20} className="text-brand-400" />
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Tool Breakdown</h3>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {m?.tools.by_tool && Object.keys(m.tools.by_tool).length > 0 ? (
              Object.entries(m.tools.by_tool).map(([toolName, count]) => (
                <div key={toolName} className="flex items-center justify-between rounded-2xl bg-slate-950/70 p-3 text-xs border border-white/5">
                  <span className="font-semibold text-slate-200">{toolName}</span>
                  <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-brand-300 font-mono">{count} calls</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic">No tools executed yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
