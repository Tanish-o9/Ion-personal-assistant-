import { motion } from 'framer-motion';

const statuses = [
  { label: 'Listening', color: 'bg-cyan-500/10 text-cyan-300' },
  { label: 'Thinking', color: 'bg-amber-500/10 text-amber-300' },
  { label: 'Responding', color: 'bg-emerald-500/10 text-emerald-300' },
  { label: 'Offline', color: 'bg-rose-500/10 text-rose-300' },
];

export default function JarvisStatusCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">System Status</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Ion Pulse</h3>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-slate-300">
          <span className="block font-semibold text-white">Live AI</span>
          <span className="text-xs text-slate-500">Enterprise mode</span>
        </div>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-2">
        {statuses.map((status) => (
          <div key={status.label} className={`rounded-3xl border border-white/5 p-4 ${status.color}`}>
            <span className="block text-sm font-semibold text-white">{status.label}</span>
            <span className="mt-2 block text-xs text-slate-400">Dynamic mode enabled for AI flow.</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
