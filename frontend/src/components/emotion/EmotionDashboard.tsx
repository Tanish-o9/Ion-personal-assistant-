import { useContext, useMemo } from 'react';
import { motion } from 'framer-motion';
import { AssistantContext } from '../../contexts/AssistantContext';
import { EmotionLabel } from '../../types';

const emotionPalette: Record<EmotionLabel, string> = {
  Happy: 'bg-emerald-500',
  Sad: 'bg-sky-500',
  Angry: 'bg-rose-500',
  Calm: 'bg-cyan-500',
  Excited: 'bg-fuchsia-500',
  Curious: 'bg-violet-500',
  Professional: 'bg-slate-400',
  Supportive: 'bg-teal-400',
  Friendly: 'bg-amber-400',
  Motivated: 'bg-orange-400',
  Energetic: 'bg-pink-400',
  Confused: 'bg-indigo-400',
};

const emotionHistory: { label: EmotionLabel; confidence: number }[] = [
  { label: 'Curious', confidence: 0.8 },
  { label: 'Calm', confidence: 0.92 },
  { label: 'Professional', confidence: 0.74 },
  { label: 'Friendly', confidence: 0.65 },
];

export default function EmotionDashboard() {
  const { emotion } = useContext(AssistantContext);
  const topEmotions = useMemo(() => emotionHistory.slice(0, 4), []);

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/75 p-6 shadow-futuristic">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Emotion Engine</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Mood and intent analysis</h3>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-200">
          <p className="font-semibold text-white">Current</p>
          <p className="mt-1 text-slate-400">{emotion.label}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-5">
          <p className="text-sm text-slate-400">Detected emotion</p>
          <h4 className="mt-3 text-3xl font-semibold text-white">{emotion.label}</h4>
          <div className="mt-6 h-4 overflow-hidden rounded-full bg-slate-800">
            <div className={`h-full ${emotionPalette[emotion.label]} transition-all`} style={{ width: `${Math.round(emotion.confidence * 100)}%` }} />
          </div>
          <p className="mt-3 text-sm text-slate-400">Confidence {Math.round(emotion.confidence * 100)}%</p>
        </div>

        <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-5">
          <p className="text-sm text-slate-400">Emotion history</p>
          <div className="mt-6 space-y-4">
            {topEmotions.map((item) => (
              <div key={item.label} className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-white">{item.label}</p>
                  <p className="text-xs text-slate-500">Confidence {Math.round(item.confidence * 100)}%</p>
                </div>
                <span className={`rounded-full px-3 py-2 text-xs font-semibold text-white ${emotionPalette[item.label]}`}>
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
