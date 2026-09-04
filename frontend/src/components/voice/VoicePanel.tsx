import { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineMicrophone, HiOutlineVolumeUp } from 'react-icons/hi';
import { AssistantContext } from '../../contexts/AssistantContext';
import { postVoice } from '../../services/voiceService';

const statusMap = {
  idle: { label: 'Idle', color: 'bg-slate-700 text-slate-200' },
  listening: { label: 'Listening', color: 'bg-cyan-500/15 text-cyan-200' },
  processing: { label: 'Processing', color: 'bg-amber-500/15 text-amber-200' },
  speaking: { label: 'Speaking', color: 'bg-emerald-500/15 text-emerald-200' },
  offline: { label: 'Offline', color: 'bg-rose-500/15 text-rose-200' },
};

const SpeechRecognition = typeof window !== 'undefined' ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition : null;

export default function VoicePanel() {
  const { currentModel, voiceStatus, setVoiceStatus, addMessage } = useContext(AssistantContext);
  const recognitionRef = useRef<any | null>(null);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');

  const voiceStatusRef = useRef(voiceStatus);
  useEffect(() => {
    voiceStatusRef.current = voiceStatus;
  }, [voiceStatus]);

  const handleVoiceResponse = useCallback(
    async (finalTranscript: string) => {
      if (!finalTranscript.trim()) {
        setVoiceStatus('idle');
        return;
      }

      try {
        const response = await postVoice({ audioInput: finalTranscript, model: currentModel });
        addMessage({ role: 'assistant', content: response.message.content });
        setVoiceStatus('speaking');
        window.setTimeout(() => setVoiceStatus('idle'), 1200);
      } catch (err: any) {
        setError(err?.message || 'Voice API call failed.');
        setVoiceStatus('offline');
      }
    },
    [addMessage, currentModel, setVoiceStatus]
  );

  useEffect(() => {
    if (!SpeechRecognition) {
      setError('Voice capture is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

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
      }

      if (finalTranscript) {
        setTranscript(finalTranscript);
        setVoiceStatus('processing');
        addMessage({ role: 'user', content: finalTranscript });
        handleVoiceResponse(finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      setError(`Voice recognition error: ${event.error || 'unknown error'}`);
      setVoiceStatus('offline');
    };

    recognition.onend = () => {
      if (voiceStatusRef.current === 'listening') {
        setVoiceStatus('idle');
      }
    };

    recognitionRef.current = recognition;
    return () => recognition.stop?.();
  }, [handleVoiceResponse, addMessage, setVoiceStatus]);

  const toggleListening = () => {
    setError('');

    if (!SpeechRecognition) {
      setError('Voice capture not available on this device.');
      setVoiceStatus('offline');
      return;
    }

    if (voiceStatus === 'listening') {
      recognitionRef.current?.stop();
      return;
    }

    try {
      setTranscript('');
      setVoiceStatus('listening');
      recognitionRef.current?.start();
    } catch (err) {
      setError('Failed to start voice capture. Please allow microphone access.');
      setVoiceStatus('offline');
    }
  };

  const status = statusMap[voiceStatus];

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/75 p-6 shadow-futuristic">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Voice Assistant</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Ion Audio Hub</h3>
        </div>
        <span className={`rounded-full px-4 py-2 text-xs font-semibold tracking-[0.15em] ${status.color}`}>
          {status.label}
        </span>
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-[1fr_auto]">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={toggleListening}
          className="group relative inline-flex items-center justify-center rounded-[1.75rem] bg-brand-500 px-6 py-5 font-semibold text-slate-950 shadow-lg shadow-brand-500/30 transition hover:bg-brand-400"
        >
          <span className="absolute inset-0 rounded-[1.75rem] bg-gradient-to-br from-brand-400 to-cyan-400 opacity-50 blur-xl transition group-hover:opacity-80" />
          <HiOutlineMicrophone size={22} className="relative z-10" />
          <span className="relative z-10 ml-3">
            {voiceStatus === 'listening' ? 'Stop listening' : 'Activate Voice'}
          </span>
        </motion.button>

        <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/80 p-5">
          <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-cyan-400 via-brand-500 to-violet-400 opacity-40" />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Captured text</p>
              <p className="mt-2 text-base text-slate-200">Live speech transcription</p>
            </div>
            <HiOutlineVolumeUp size={26} className="text-cyan-300" />
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-300 min-h-[120px]">
            {transcript || 'Speak into your microphone once voice capture is active.'}
          </div>
          {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}
        </div>
      </div>
    </div>
  );
}
