import { useContext } from 'react';
import { AssistantContext } from '../contexts/AssistantContext';
import { ModelOption } from '../types';

const models: ModelOption[] = ['claude', 'huggingFace', 'gemini', 'openai'];

export default function SettingsPage() {
  const { currentModel, setModel } = useContext(AssistantContext);

  return (
    <div className="grid gap-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-futuristic">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">System settings</p>
        <h2 className="mt-3 text-3xl font-semibold text-white">Ion configuration</h2>
        <p className="mt-3 text-sm leading-7 text-slate-400">Adjust AI models, voice controls, memory behavior, and theme preferences from a single panel.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-futuristic">
          <h3 className="text-xl font-semibold text-white">AI Models</h3>
          <p className="mt-2 text-sm text-slate-400">Choose the primary model used by Ion and a backup fallback path.</p>
          <div className="mt-6 space-y-3">
            {models.map((model) => (
              <button
                key={model}
                onClick={() => setModel(model)}
                className={`w-full rounded-3xl border px-4 py-4 text-left text-sm transition ${
                  currentModel === model
                    ? 'border-brand-400/40 bg-brand-500/15 text-white'
                    : 'border-white/10 bg-slate-900/80 text-slate-300 hover:border-brand-400/30 hover:bg-slate-900/90'
                }`}
              >
                <span className="font-semibold uppercase tracking-[0.15em]">{model}</span>
                <p className="mt-1 text-xs text-slate-500">{model === currentModel ? 'Active model' : 'Toggle to use'}</p>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-futuristic">
          <h3 className="text-xl font-semibold text-white">Voice & memory</h3>
          <div className="mt-6 space-y-5 text-sm text-slate-300">
            <div className="rounded-3xl border border-white/5 bg-slate-900/80 p-4">
              <p className="font-semibold text-white">Voice selection</p>
              <p className="mt-2 text-slate-400">Choose Ion's speaking style, speed, pitch, and volume from the voice engine.</p>
            </div>
            <div className="rounded-3xl border border-white/5 bg-slate-900/80 p-4">
              <p className="font-semibold text-white">Memory settings</p>
              <p className="mt-2 text-slate-400">Clear or export memory, configure retention rules, and define session behavior.</p>
            </div>
            <div className="rounded-3xl border border-white/5 bg-slate-900/80 p-4">
              <p className="font-semibold text-white">Theme mode</p>
              <p className="mt-2 text-slate-400">Ion is optimized for dark mode with neon glassmorphism and animated gradients.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
