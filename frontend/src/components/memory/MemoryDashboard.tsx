import { useContext } from 'react';
import { AssistantContext } from '../../contexts/AssistantContext';
import { motion } from 'framer-motion';

export default function MemoryDashboard() {
  const { memoryEntries, deleteMemoryEntry, clearMemory } = useContext(AssistantContext);

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Memory Dashboard</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Short-term & long-term recall</h3>
        </div>
        <button onClick={clearMemory} className="rounded-3xl border border-slate-700 px-4 py-3 text-sm text-slate-300 transition hover:border-brand-400 hover:text-brand-200">
          Clear Memory
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {memoryEntries.length ? (
          memoryEntries.map((entry) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-3xl border border-white/5 bg-slate-950/80 p-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{entry.category === 'short-term' ? 'Session memory' : 'Long-term memory'}</p>
                  <p className="mt-1 font-semibold text-white">{entry.title}</p>
                </div>
                <button
                  onClick={() => deleteMemoryEntry(entry.id)}
                  className="rounded-2xl border border-rose-400/10 px-3 py-2 text-xs text-rose-300 transition hover:border-rose-300/30"
                >
                  Delete
                </button>
              </div>
              <p className="mt-4 text-sm leading-7 text-slate-300">{entry.value}</p>
              <p className="mt-4 text-xs text-slate-500">{new Date(entry.createdAt).toLocaleString()}</p>
            </motion.div>
          ))
        ) : (
          <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-950/80 p-10 text-center text-slate-500">
            No memory entries yet. Start a conversation to capture Jarvis memory.
          </div>
        )}
      </div>
    </div>
  );
}
