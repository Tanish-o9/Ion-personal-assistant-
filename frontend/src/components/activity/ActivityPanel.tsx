import { HiOutlineLightningBolt } from 'react-icons/hi';

interface ActivityPanelProps {
  events: string[];
  isConnected: boolean;
}

export default function ActivityPanel({ events, isConnected }: ActivityPanelProps) {
  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-500/15 text-brand-300 ring-1 ring-brand-400/20">
            <HiOutlineLightningBolt size={20} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Live Telemetry</p>
            <h3 className="text-lg font-semibold text-white">ION Activity</h3>
          </div>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold tracking-wider ${
            isConnected ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30' : 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30'
          }`}
        >
          {isConnected ? '● Connected' : '○ Disconnected'}
        </span>
      </div>

      <div className="mt-4 max-h-[220px] space-y-2 overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/90 p-4 text-xs font-mono">
        {events.length > 0 ? (
          events.map((event, idx) => (
            <div key={idx} className="flex items-start gap-2 text-slate-300">
              <span className="shrink-0 text-slate-500">[{new Date().toLocaleTimeString()}]</span>
              <span className="break-all">{event}</span>
            </div>
          ))
        ) : (
          <div className="py-8 text-center text-slate-500 font-sans italic">
            Waiting for activity events...
          </div>
        )}
      </div>
    </div>
  );
}
