import MemoryPanel from '../components/memory/MemoryPanel';

interface MemoryPageProps {
  userId: string;
}

export default function MemoryPage({ userId }: MemoryPageProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic">
        <h2 className="text-2xl font-semibold text-white">ION Long-Term Memory</h2>
        <p className="mt-1 text-xs text-slate-400">
          View user preferences, active projects, and custom instructions saved across sessions.
        </p>
      </div>

      <MemoryPanel userId={userId} />
    </div>
  );
}
