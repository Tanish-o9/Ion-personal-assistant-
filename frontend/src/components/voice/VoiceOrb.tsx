import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { VoiceStatus } from '../../types';

interface VoiceOrbProps {
  status: VoiceStatus;
}

export default function VoiceOrb({ status }: VoiceOrbProps) {
  const orbConfig = useMemo(() => {
    switch (status) {
      case 'wake_listening':
      case 'idle':
        return {
          glowColor: 'from-indigo-500/30 via-brand-500/20 to-purple-600/30',
          borderColor: 'border-indigo-500/40',
          pulseScale: [1, 1.05, 1],
          pulseDuration: 4,
          label: 'Listening for "Hey Ion"',
          particleColor: 'bg-indigo-400',
        };
      case 'wake_detected':
        return {
          glowColor: 'from-cyan-400/40 via-brand-400/30 to-blue-500/40',
          borderColor: 'border-cyan-400 ring-4 ring-cyan-500/20',
          pulseScale: [1, 1.15, 1],
          pulseDuration: 0.8,
          label: 'Wake Phrase Detected!',
          particleColor: 'bg-cyan-300',
        };
      case 'listening':
      case 'speech_detected':
      case 'user_speaking':
        return {
          glowColor: 'from-cyan-500/50 via-emerald-400/30 to-teal-500/50',
          borderColor: 'border-cyan-400 ring-8 ring-cyan-500/30',
          pulseScale: [1, 1.18, 0.98, 1.12, 1],
          pulseDuration: 1.2,
          label: 'Listening to your speech...',
          particleColor: 'bg-cyan-400',
        };
      case 'end_of_turn':
      case 'transcribing':
      case 'processing':
      case 'responding':
        return {
          glowColor: 'from-purple-500/50 via-brand-500/40 to-amber-500/40',
          borderColor: 'border-purple-400 ring-6 ring-purple-500/30',
          pulseScale: [1, 1.1, 1],
          pulseDuration: 1.5,
          label: 'ION is reasoning...',
          particleColor: 'bg-purple-300',
        };
      case 'speaking':
        return {
          glowColor: 'from-emerald-400/50 via-teal-400/40 to-cyan-500/40',
          borderColor: 'border-emerald-400 ring-8 ring-emerald-500/30',
          pulseScale: [1, 1.14, 0.96, 1.1, 1],
          pulseDuration: 1.0,
          label: 'ION is speaking...',
          particleColor: 'bg-emerald-300',
        };
      case 'offline':
      default:
        return {
          glowColor: 'from-rose-500/20 via-slate-800 to-slate-900',
          borderColor: 'border-rose-500/30',
          pulseScale: [1, 1.02, 1],
          pulseDuration: 3,
          label: 'Voice System Offline',
          particleColor: 'bg-rose-400',
        };
    }
  }, [status]);

  return (
    <div className="relative flex flex-col items-center justify-center py-10">
      {/* Outer ambient aura glow */}
      <motion.div
        animate={{
          scale: orbConfig.pulseScale,
          opacity: [0.5, 0.8, 0.5],
        }}
        transition={{
          duration: orbConfig.pulseDuration,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`absolute h-72 w-72 rounded-full bg-gradient-to-tr ${orbConfig.glowColor} blur-3xl`}
      />

      {/* Outer Ring 1 */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
        className="absolute h-64 w-64 rounded-full border border-white/10 border-t-brand-400/50"
      />

      {/* Outer Ring 2 */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 18, repeat: Infinity, ease: 'linear' }}
        className="absolute h-52 w-52 rounded-full border border-dashed border-white/15 border-b-cyan-400/50"
      />

      {/* Central Interactive Voice Orb Core */}
      <motion.div
        animate={{ scale: orbConfig.pulseScale }}
        transition={{
          duration: orbConfig.pulseDuration,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`relative z-10 flex h-40 w-40 items-center justify-center rounded-full border ${orbConfig.borderColor} bg-slate-950/90 shadow-2xl backdrop-blur-2xl`}
      >
        <div className={`h-24 w-24 rounded-full bg-gradient-to-tr ${orbConfig.glowColor} opacity-90 blur-md`} />
        <div className="absolute flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              animate={
                status === 'speaking' || status === 'user_speaking' || status === 'listening'
                  ? { height: ['12px', '36px', '16px', '42px', '12px'] }
                  : { height: ['8px', '14px', '8px'] }
              }
              transition={{
                duration: 0.6 + i * 0.1,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              className={`w-1.5 rounded-full ${orbConfig.particleColor}`}
            />
          ))}
        </div>
      </motion.div>

      {/* Orbiting particles */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
        className="absolute h-48 w-48"
      >
        <div className={`h-2.5 w-2.5 rounded-full ${orbConfig.particleColor} shadow-lg blur-[1px]`} />
      </motion.div>
    </div>
  );
}
