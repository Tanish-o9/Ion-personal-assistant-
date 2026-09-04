import { HiOutlineExternalLink, HiOutlineLibrary } from 'react-icons/hi';
import { ResearchSourceItem } from '../../hooks/useWebSocket';

interface SourcesPanelProps {
  sources: ResearchSourceItem[];
}

export default function SourcesPanel({ sources }: SourcesPanelProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex items-center gap-3 mb-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-400/20">
          <HiOutlineLibrary size={20} />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Information Retrieval</p>
          <h3 className="text-lg font-semibold text-white">Research & RAG Sources ({sources.length})</h3>
        </div>
      </div>

      <div className="space-y-3">
        {sources.map((s, idx) => (
          <div key={idx} className="rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs">
            <div className="flex items-center justify-between gap-2 font-semibold text-indigo-200">
              <span className="truncate">{s.title || s.url}</span>
              {s.url && (
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-brand-400 hover:underline shrink-0"
                >
                  Visit <HiOutlineExternalLink size={12} />
                </a>
              )}
            </div>
            {s.snippet && <p className="mt-2 text-slate-300 line-clamp-3 leading-relaxed">{s.snippet}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
