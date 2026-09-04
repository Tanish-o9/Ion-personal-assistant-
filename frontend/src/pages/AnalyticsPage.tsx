import AnalyticsOverview from '../components/analytics/AnalyticsOverview';

export default function AnalyticsPage() {
  return (
    <div className="grid gap-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-futuristic">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Analytics hub</p>
        <h2 className="mt-3 text-3xl font-semibold text-white">AI usage metrics</h2>
        <p className="mt-3 text-sm leading-7 text-slate-400">Monitor conversations, memory growth, and API utilization with enterprise-grade insights.</p>
      </div>
      <AnalyticsOverview />
    </div>
  );
}
