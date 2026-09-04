import EmotionDashboard from '../components/emotion/EmotionDashboard';

export default function EmotionPage() {
  return (
    <div className="grid gap-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-futuristic">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Emotion analytics</p>
        <h2 className="mt-3 text-3xl font-semibold text-white">ION emotional insight</h2>
        <p className="mt-3 text-sm leading-7 text-slate-400">Explore how ION reads the mood, confidence, and response style through your conversation history.</p>
      </div>
      <EmotionDashboard />
    </div>
  );
}
