import { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineMicrophone, HiOutlineVolumeUp, HiOutlineSparkles } from 'react-icons/hi';
import { AssistantContext } from '../../contexts/AssistantContext';
import { postVoice } from '../../services/voiceService';
import { VoiceStateMachine } from '../../services/voiceStateMachine';
import { WakeWordDetectorClient } from '../../services/wakeWordDetector';
import { VoiceStatus } from '../../types';

const statusMap: Record<VoiceStatus, { label: string; color: string }> = {
  idle: { label: 'Idle', color: 'bg-slate-700 text-slate-200' },
  wake_listening: { label: 'Listening for "Hey Ion"', color: 'bg-indigo-500/20 text-indigo-200 ring-1 ring-indigo-500/40 animate-pulse' },
  wake_detected: { label: 'Wake Phrase Detected!', color: 'bg-cyan-500/25 text-cyan-200 ring-1 ring-cyan-400' },
  listening: { label: "I'm listening...", color: 'bg-cyan-500/20 text-cyan-200 ring-1 ring-cyan-500/40' },
  speech_detected: { label: 'Speech Detected', color: 'bg-emerald-500/20 text-emerald-200' },
  user_speaking: { label: 'Listening...', color: 'bg-emerald-500/30 text-emerald-200 ring-1 ring-emerald-400' },
  end_of_turn: { label: 'Finalizing Speech...', color: 'bg-amber-500/20 text-amber-200' },
  transcribing: { label: 'Transcribing...', color: 'bg-amber-500/20 text-amber-200' },
  processing: { label: 'Thinking...', color: 'bg-purple-500/20 text-purple-200 ring-1 ring-purple-500/40 animate-pulse' },
  responding: { label: 'Generating Response...', color: 'bg-purple-500/20 text-purple-200' },
  speaking: { label: 'ION Speaking...', color: 'bg-emerald-500/20 text-emerald-200 ring-1 ring-emerald-500/40' },
  offline: { label: 'Voice Offline', color: 'bg-rose-500/20 text-rose-200' },
};

const SpeechRecognition = typeof window !== 'undefined' ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition : null;

export default function VoicePanel() {
  const { currentModel, voiceStatus, setVoiceStatus, addMessage } = useContext(AssistantContext);
  const [handsFreeEnabled, setHandsFreeEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');

  const recognitionRef = useRef<any | null>(null);
  const wakeDetectorRef = useRef<WakeWordDetectorClient | null>(null);
  const stateMachineRef = useRef<VoiceStateMachine | null>(null);

  const voiceStatusRef = useRef(voiceStatus);
  useEffect(() => {
    voiceStatusRef.current = voiceStatus;
  }, [voiceStatus]);

  // Initialize Voice State Machine
  useEffect(() => {
    stateMachineRef.current = new VoiceStateMachine({
      silenceTimeoutMs: 1500,
      minSpeechDurationMs: 300,
      maxTurnDurationMs: 30000,
      onStateChange: (newState) => {
        const mappedStatus = newState.toLowerCase() as VoiceStatus;
        setVoiceStatus(mappedStatus);
      },
    });
  }, [setVoiceStatus]);

  const handleVoiceResponse = useCallback(
    async (finalTranscript: string) => {
      const cleanTranscript = finalTranscript
        .replace(/^hey ion[\s,.]*/i, '')
        .replace(/^ion[\s,.]*/i, '')
        .trim();

      const textToSend = cleanTranscript || finalTranscript.trim();

      if (!textToSend) {
        stateMachineRef.current?.resetToWakeListening();
        return;
      }

      try {
        stateMachineRef.current?.transitionTo('PROCESSING');
        const response = await postVoice({ audioInput: textToSend, model: currentModel });
        addMessage({ role: 'assistant', content: response.message.content });
        stateMachineRef.current?.transitionTo('SPEAKING');

        // Play audio TTS or simulate speaking turn duration
        const synth = window.speechSynthesis;
        if (synth && 'SpeechSynthesisUtterance' in window) {
          const utterance = new SpeechSynthesisUtterance(response.message.content);
          utterance.onend = () => {
            if (handsFreeEnabled) {
              stateMachineRef.current?.resetToWakeListening();
            } else {
              stateMachineRef.current?.stop();
            }
          };
          utterance.onerror = () => {
            if (handsFreeEnabled) {
              stateMachineRef.current?.resetToWakeListening();
            } else {
              stateMachineRef.current?.stop();
            }
          };
          synth.speak(utterance);
        } else {
          window.setTimeout(() => {
            if (handsFreeEnabled) {
              stateMachineRef.current?.resetToWakeListening();
            } else {
              stateMachineRef.current?.stop();
            }
          }, 2000);
        }
      } catch (err: any) {
        setError(err?.message || 'Voice pipeline execution failed.');
        stateMachineRef.current?.transitionTo('ERROR');
      }
    },
    [addMessage, currentModel, handsFreeEnabled]
  );

  // Setup Web Speech Recognition
  useEffect(() => {
    if (!SpeechRecognition) {
      setError('Voice capture is not supported in this browser.');
      setVoiceStatus('offline');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      if (interimTranscript) {
        setTranscript(interimTranscript);
        stateMachineRef.current?.onSpeechStart();
      }

      if (finalTranscript) {
        setTranscript(finalTranscript);
        stateMachineRef.current?.transitionTo('END_OF_TURN');
        addMessage({ role: 'user', content: finalTranscript });
        handleVoiceResponse(finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      if (event.error === 'no-speech') return;
      setError(`Voice recognition error: ${event.error || 'unknown error'}`);
    };

    recognition.onend = () => {
      if (handsFreeEnabled && voiceStatusRef.current === 'wake_listening') {
        try {
          recognition.start();
        } catch (_) {}
      }
    };

    recognitionRef.current = recognition;
    return () => recognition.stop?.();
  }, [handleVoiceResponse, addMessage, setVoiceStatus, handsFreeEnabled]);

  // Hands-free mode automatic start
  useEffect(() => {
    if (handsFreeEnabled && SpeechRecognition) {
      wakeDetectorRef.current = new WakeWordDetectorClient({
        wakePhrase: 'hey ion',
        onWakeWordDetected: () => {
          stateMachineRef.current?.transitionTo('WAKE_DETECTED');
          setTimeout(() => {
            stateMachineRef.current?.transitionTo('LISTENING');
            try {
              recognitionRef.current?.start();
            } catch (_) {}
          }, 300);
        },
      });

      wakeDetectorRef.current.start();
      stateMachineRef.current?.resetToWakeListening();
    } else {
      wakeDetectorRef.current?.stop();
    }

    return () => {
      wakeDetectorRef.current?.stop();
    };
  }, [handsFreeEnabled]);

  const toggleHandsFree = () => {
    setHandsFreeEnabled((prev) => !prev);
    setError('');
  };

  const status = statusMap[voiceStatus] || statusMap['idle'];

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/75 p-6 shadow-futuristic">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">ION Hands-Free Voice</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Ion Audio Hub</h3>
        </div>
        <span className={`rounded-full px-4 py-2 text-xs font-semibold tracking-[0.15em] ${status.color}`}>
          {status.label}
        </span>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-[1fr_auto]">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={toggleHandsFree}
          className={`group relative inline-flex items-center justify-center rounded-[1.75rem] px-6 py-5 font-semibold transition ${
            handsFreeEnabled
              ? 'bg-brand-500 text-slate-950 shadow-lg shadow-brand-500/30 hover:bg-brand-400'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <span className="absolute inset-0 rounded-[1.75rem] bg-gradient-to-br from-brand-400 to-cyan-400 opacity-30 blur-xl transition group-hover:opacity-60" />
          <HiOutlineSparkles size={22} className="relative z-10" />
          <span className="relative z-10 ml-3">
            {handsFreeEnabled ? 'Hands-Free Mode Enabled ("Hey Ion")' : 'Enable Hands-Free Voice'}
          </span>
        </motion.button>

        <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/80 p-5">
          <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-cyan-400 via-brand-500 to-violet-400 opacity-40" />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Live Voice Turn</p>
              <p className="mt-2 text-base text-slate-200">Say "Hey Ion" to activate without pressing buttons</p>
            </div>
            <HiOutlineVolumeUp size={26} className="text-cyan-300" />
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-300 min-h-[120px]">
            {transcript || (handsFreeEnabled ? 'Listening for "Hey Ion"...' : 'Activate Hands-Free Mode above.')}
          </div>
          {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}
        </div>
      </div>
    </div>
  );
}
