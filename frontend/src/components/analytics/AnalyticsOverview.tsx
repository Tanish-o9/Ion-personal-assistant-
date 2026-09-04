import { useQuery } from '@tanstack/react-query';
import { getAnalytics } from '../../services/analyticsService';
import { AnalyticsSummary } from '../../types';

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-5">
      <p className="text-sm uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <p className="mt-4 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
}

function EmotionBar({ emotion, value }: { emotion: string; value: number }) {
  const width = `${Math.min(100, Math.round(value))}%`;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm text-slate-300">
        <span>{emotion}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-brand-500 transition-all" style={{ width }} />
      </div>
    </div>
  );
}

const defaultStats: AnalyticsSummary = {
  totalConversations: 18,
  memoryEntries: 9,
  apiUsage: 42,
  avgResponseTime: 1.9,
  emotionDistribution: {
    Happy: 22,
    Sad: 8,
    Angry: 4,
    Calm: 34,
    Excited: 10,
    Curious: 12,
    Professional: 8,
    Supportive: 7,
    Friendly: 14,
    Motivated: 16,
    Energetic: 9,
    Confused: 5,
  },
  mostUsedCommands: ['Summarize notes', 'Schedule meeting', 'Play focus music'],
};

export default function AnalyticsOverview() {
  const { data } = useQuery<AnalyticsSummary>({
    queryKey: ['analytics'],
    queryFn: getAnalytics,
    staleTime: 1000 * 60 * 5,
    retry: 1,
  });

  const stats = data ?? defaultStats;
  const emotionEntries = Object.entries(stats.emotionDistribution) as [keyof typeof stats.emotionDistribution, number][];

  return (
    <div className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total conversations" value={`${stats.totalConversations}`} />
        <MetricCard label="Memory entries" value={`${stats.memoryEntries}`} />
        <MetricCard label="API usage" value={`${stats.apiUsage} calls`} />
        <MetricCard label="Avg. response" value={`${stats.avgResponseTime}s`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_1.2fr]">
        <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Emotion distribution</p>
          <div className="mt-6 space-y-4">
            {emotionEntries.slice(0, 6).map(([emotion, value]) => (
              <EmotionBar key={emotion} emotion={String(emotion)} value={value} />
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-futuristic">
          <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Most used commands</p>
          <div className="mt-6 space-y-3">
            {stats.mostUsedCommands.map((command: string) => (
              <div key={command} className="rounded-3xl border border-white/5 bg-slate-900/80 p-4 text-sm text-slate-200">
                {command}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
