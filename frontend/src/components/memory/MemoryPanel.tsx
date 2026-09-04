import { useEffect, useState, useCallback } from 'react';
import { HiOutlineBookmark, HiOutlineTrash, HiOutlineRefresh } from 'react-icons/hi';
import { fetchUserMemories, deleteUserMemory } from '../../services/api';

interface MemoryItem {
  id: string;
  user_id: string;
  content: string;
  memory_type: string;
  importance: number;
  created_at: string;
}

interface MemoryPanelProps {
  userId?: string;
}

export default function MemoryPanel({ userId = 'default_user' }: MemoryPanelProps) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadMemories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUserMemories(userId);
      setMemories(data || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to load user memories.');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const handleDelete = async (memoryId: string) => {
    try {
      await deleteUserMemory(userId, memoryId);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
    } catch (err: any) {
      setError(err?.message || 'Failed to delete memory.');
    }
  };

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15 text-amber-300 ring-1 ring-amber-400/20">
            <HiOutlineBookmark size={20} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Memory Layer</p>
            <h3 className="text-lg font-semibold text-white">Persistent User Memories</h3>
          </div>
        </div>

        <button
          onClick={loadMemories}
          className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-950 p-2 text-xs text-slate-300 hover:border-brand-400"
        >
          <HiOutlineRefresh size={14} /> Refresh
        </button>
      </div>

      {loading ? (
        <p className="py-8 text-center text-xs text-slate-500">Loading user memory records...</p>
      ) : error ? (
        <p className="py-4 text-xs text-rose-400">{error}</p>
      ) : memories.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500 italic">
          No persistent memories extracted yet. ION automatically learns preferences from conversation.
        </div>
      ) : (
        <div className="space-y-3">
          {memories.map((m) => (
            <div key={m.id} className="flex items-start justify-between gap-3 rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="rounded-md bg-slate-800 px-2 py-0.5 font-semibold text-[10px] text-amber-300 uppercase">
                    {m.memory_type}
                  </span>
                  <span className="text-[10px] text-slate-500">Importance: {m.importance}/5</span>
                </div>
                <p className="text-slate-200">{m.content}</p>
              </div>

              <button
                onClick={() => handleDelete(m.id)}
                className="text-slate-500 hover:text-rose-400 transition p-1"
                title="Delete memory"
              >
                <HiOutlineTrash size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
