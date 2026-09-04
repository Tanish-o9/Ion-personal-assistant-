import { useContext } from 'react';
import { HiOutlineSparkles, HiOutlineVolumeUp, HiOutlineMicrophone } from 'react-icons/hi';
import VoiceOrb from './VoiceOrb';
import { AssistantContext } from '../../contexts/AssistantContext';

interface VoiceCoreProps {
  transcript: string;
  response: string | null;
  isConnected: boolean;
  onCancel?: () => void;
}

const statusTextMap: Record<string, string> = {
  idle: 'Listening for "Hey Ion"',
  wake_listening: 'Listening for "Hey Ion"',
  wake_detected: 'Wake Phrase Detected!',
  listening: "I'm listening...",
  speech_detected: 'Listening to your speech...',
  user_speaking: 'Listening...',
  end_of_turn: 'Finalizing Speech...',
  transcribing: 'Transcribing speech...',
  processing: 'Thinking & Reasoning...',
  responding: 'Generating Response...',
  speaking: 'ION is speaking response...',
  offline: 'Voice System Offline',
};

export default function VoiceCore({ transcript, response, isConnected, onCancel }: VoiceCoreProps) {
  const { voiceStatus } = useContext(AssistantContext);
  const currentStatusText = statusTextMap[voiceStatus] || 'Voice Ready';

  return (
    <div className="relative overflow-hidden rounded-[2.5rem] border border-white/10 bg-slate-900/80 p-8 shadow-futuristic backdrop-blur-xl">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-brand-500 via-cyan-400 to-indigo-500 opacity-60" />

      {/* Header Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500/15 text-brand-300 ring-1 ring-brand-400/20">
            <HiOutlineSparkles size={24} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-400 font-semibold">Primary Voice Engine</p>
            <h2 className="text-2xl font-bold text-white tracking-tight">ION Voice Core</h2>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {onCancel && (voiceStatus === 'speaking' || voiceStatus === 'processing') && (
            <button
              onClick={onCancel}
              className="rounded-full border border-rose-500/30 bg-rose-500/15 px-4 py-1.5 text-xs font-semibold text-rose-300 transition hover:bg-rose-500/25"
            >
              Interrupt
            </button>
          )}

          <span
            className={`rounded-full px-4 py-2 text-xs font-semibold tracking-wider ${
              isConnected
                ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30'
                : 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30'
            }`}
          >
            {isConnected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
      </div>

      {/* Central Animated Orb */}
      <VoiceOrb status={voiceStatus} />

      {/* Status Instruction Badge */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-400/20 bg-brand-500/10 px-5 py-2 text-sm font-semibold text-brand-200 shadow-inner">
          <HiOutlineMicrophone size={16} className="animate-pulse text-brand-400" />
          <span>{currentStatusText}</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">Say <span className="font-semibold text-white">"Hey Ion"</span> at any time to activate hands-free assistant</p>
      </div>

      {/* Live Transcript & Current Response Container */}
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-5 shadow-inner">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">User Speech Transcript</span>
            <HiOutlineMicrophone size={16} className="text-cyan-400" />
          </div>
          <p className="text-sm text-slate-200 min-h-[60px] leading-relaxed">
            {transcript || <span className="text-slate-500 italic">"Hey Ion..." (Speak after wake phrase)</span>}
          </p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-5 shadow-inner">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-semibold">ION Response Output</span>
            <HiOutlineVolumeUp size={16} className="text-emerald-400" />
          </div>
          <p className="text-sm text-slate-200 min-h-[60px] leading-relaxed">
            {response || <span className="text-slate-500 italic">ION response will be spoken automatically...</span>}
          </p>
        </div>
      </div>
    </div>
  );
}
