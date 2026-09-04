import { useCallback, useContext, useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineMicrophone, HiOutlineVolumeUp, HiOutlineSparkles, HiOutlineTerminal } from 'react-icons/hi';
import { AssistantContext } from '../../contexts/AssistantContext';
import { postVoice } from '../../services/voiceService';
import { VoiceStateMachine } from '../../services/voiceStateMachine';
import { WakeWordDetectorClient } from '../../services/wakeWordDetector';
import { VADEngine, VADDiagnostics } from '../../services/vadEngine';
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
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [vadInfo, setVadInfo] = useState<VADDiagnostics | null>(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  const recognitionRef = useRef<any | null>(null);
  const wakeDetectorRef = useRef<WakeWordDetectorClient | null>(null);
  const vadEngineRef = useRef<VADEngine | null>(null);
  const stateMachineRef = useRef<VoiceStateMachine | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const isFinalizingRef = useRef(false);
  const isSpeakingTtsRef = useRef(false);
  const voiceStatusRef = useRef(voiceStatus);
  const handsFreeEnabledRef = useRef(handsFreeEnabled);

  useEffect(() => {
    voiceStatusRef.current = voiceStatus;
  }, [voiceStatus]);

  useEffect(() => {
    handsFreeEnabledRef.current = handsFreeEnabled;
  }, [handsFreeEnabled]);

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

  const stopAllAudioResources = useCallback(() => {
    try {
      wakeDetectorRef.current?.stop();
    } catch (_) {}
    try {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }
    } catch (_) {}
    try {
      vadEngineRef.current?.stop();
    } catch (_) {}
    if (mediaStreamRef.current) {
      try {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      } catch (_) {}
      mediaStreamRef.current = null;
    }
  }, []);

  const handleVoiceResponse = useCallback(
    async (finalTranscript: string) => {
      if (isFinalizingRef.current) return;
      isFinalizingRef.current = true;

      const cleanTranscript = finalTranscript
        .replace(/^hey ion[\s,.]*/i, '')
        .replace(/^hi ion[\s,.]*/i, '')
        .replace(/^hey iron[\s,.]*/i, '')
        .replace(/^hey ian[\s,.]*/i, '')
        .replace(/^ion[\s,.]*/i, '')
        .trim();

      const textToSend = cleanTranscript || finalTranscript.trim();

      if (!textToSend) {
        isFinalizingRef.current = false;
        startWakeListening();
        return;
      }

      // Stop listening while processing & generating response
      try {
        if (recognitionRef.current) {
          recognitionRef.current.abort();
          recognitionRef.current = null;
        }
      } catch (_) {}
      try {
        vadEngineRef.current?.stop();
      } catch (_) {}
      try {
        wakeDetectorRef.current?.stop();
      } catch (_) {}

      try {
        stateMachineRef.current?.transitionTo('PROCESSING');
        const response = await postVoice({ audioInput: textToSend, model: currentModel });
        const responseText = response.message?.content || response.response_text || response.response || 'I am ready to help you.';
        addMessage({ role: 'assistant', content: responseText });
        stateMachineRef.current?.transitionTo('SPEAKING');
        isSpeakingTtsRef.current = true;

        const synth = window.speechSynthesis;
        if (synth && 'SpeechSynthesisUtterance' in window) {
          synth.cancel(); // Stop any pending speech
          const utterance = new SpeechSynthesisUtterance(responseText);

          const finishTts = () => {
            isSpeakingTtsRef.current = false;
            if (handsFreeEnabledRef.current) {
              startWakeListening();
            } else {
              stateMachineRef.current?.stop();
            }
          };

          utterance.onend = finishTts;
          utterance.onerror = finishTts;
          synth.speak(utterance);
        } else {
          window.setTimeout(() => {
            isSpeakingTtsRef.current = false;
            if (handsFreeEnabledRef.current) {
              startWakeListening();
            } else {
              stateMachineRef.current?.stop();
            }
          }, 2000);
        }
      } catch (err: any) {
        setErrorCode('WEBSOCKET_DISCONNECTED');
        setError(err?.message || 'Voice pipeline execution failed.');
        stateMachineRef.current?.transitionTo('ERROR');
        isFinalizingRef.current = false;
        isSpeakingTtsRef.current = false;
      }
    },
    [addMessage, currentModel]
  );

  const createAndStartRecognition = useCallback(() => {
    if (!SpeechRecognition || isSpeakingTtsRef.current) return;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (_) {}
      recognitionRef.current = null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = typeof navigator !== 'undefined' && navigator.language ? navigator.language : 'en-US';

    let lastInterimText = '';

    recognition.onstart = () => {
      console.log('[ION VOICE] SpeechRecognition session active.');
      setError('');
      setErrorCode(null);
    };

    recognition.onresult = (event: any) => {
      if (isSpeakingTtsRef.current) return;
      setError('');
      setErrorCode(null);

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
        lastInterimText = interimTranscript;
        setTranscript(interimTranscript);
        stateMachineRef.current?.onSpeechStart();
      }

      if (finalTranscript && !isFinalizingRef.current) {
        const cleanText = finalTranscript.trim();
        if (cleanText.length > 0) {
          lastInterimText = '';
          setTranscript(cleanText);
          stateMachineRef.current?.transitionTo('END_OF_TURN');
          addMessage({ role: 'user', content: cleanText });
          handleVoiceResponse(cleanText);
        }
      }
    };

  // Finalization & Transcribing Safety Guard: Prevents UI getting stuck in "Finalizing Speech..."
  useEffect(() => {
    if (voiceStatus === 'end_of_turn' || voiceStatus === 'transcribing') {
      const safetyGuard = setTimeout(() => {
        if (voiceStatusRef.current === 'end_of_turn' || voiceStatusRef.current === 'transcribing') {
          console.warn('[ION VOICE] Speech finalization safety guard triggered (4s timeout). Auto-resuming wake listening...');
          isFinalizingRef.current = false;
          if (handsFreeEnabledRef.current) {
            startWakeListening();
          }
        }
      }, 4000);
      return () => clearTimeout(safetyGuard);
    }
  }, [voiceStatus, startWakeListening]);

  recognition.onerror = (event: any) => {
      if (event.error === 'no-speech' || event.error === 'aborted' || event.error === 'audio-capture') {
        console.log(`[ION VOICE] Transient recognition state: ${event.error}`);
        return;
      }
      console.warn('[ION VOICE] Speech recognition warning/error:', event.error);
      if (event.error === 'not-allowed') {
        setErrorCode('MIC_PERMISSION_DENIED');
        setError('Microphone permission denied.');
      } else if (event.error === 'network') {
        console.warn('[ION VOICE] Web Speech API network warning. Scheduling auto-reconnection...');
        setErrorCode('NETWORK_ERROR');
        setError('Speech recognition network warning. Auto-reconnecting voice recognition...');
        setTimeout(() => {
          if (handsFreeEnabledRef.current && !isSpeakingTtsRef.current && !isFinalizingRef.current) {
            startWakeListening();
          }
        }, 600);
      } else {
        setErrorCode('SPEECH_RECOGNITION_ERROR');
      }
    };

    recognition.onend = () => {
      if (isSpeakingTtsRef.current) return;

      if (!isFinalizingRef.current && lastInterimText.trim().length > 0 && (voiceStatusRef.current === 'user_speaking' || voiceStatusRef.current === 'speech_detected')) {
        const textToProcess = lastInterimText.trim();
        lastInterimText = '';
        setTranscript(textToProcess);
        stateMachineRef.current?.transitionTo('END_OF_TURN');
        addMessage({ role: 'user', content: textToProcess });
        handleVoiceResponse(textToProcess);
        return;
      }

      if (
        handsFreeEnabledRef.current &&
        !isFinalizingRef.current &&
        (voiceStatusRef.current === 'listening' || voiceStatusRef.current === 'user_speaking')
      ) {
        try {
          recognition.start();
        } catch (_) {}
      }
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
      console.log('[ION VOICE] SpeechRecognition instance started cleanly.');
    } catch (err) {
      console.warn('[ION VOICE] Failed to start SpeechRecognition:', err);
    }
  }, [addMessage, handleVoiceResponse]);

  const startWakeListening = useCallback(async () => {
    if (!handsFreeEnabledRef.current || !SpeechRecognition || isSpeakingTtsRef.current) return;

    if (!mediaStreamRef.current && navigator.mediaDevices?.getUserMedia) {
      try {
        console.log('[ION VOICE] Requesting microphone stream getUserMedia({ audio: true })...');
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaStreamRef.current = stream;
        setError('');
        setErrorCode(null);
        console.log('[ION VOICE] Microphone permission granted.');
        console.log(`[ION VOICE] Audio stream active: ${stream.active}, Audio tracks: ${stream.getAudioTracks().length}`);
      } catch (err: any) {
        console.warn('[ION VOICE] Microphone permission pending or denied:', err);
        setErrorCode('MIC_PERMISSION_DENIED');
        setError('Microphone permission required. Please click "Allow" in browser pop-up.');
        setVoiceStatus('offline');
        return;
      }
    }

    isFinalizingRef.current = false;
    try {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }
    } catch (_) {}
    try {
      vadEngineRef.current?.stop();
    } catch (_) {}

    stateMachineRef.current?.resetToWakeListening();

    if (!wakeDetectorRef.current) {
      wakeDetectorRef.current = new WakeWordDetectorClient({
        wakePhrase: 'hey ion',
        onWakeWordDetected: (fullTranscript) => {
          if (isFinalizingRef.current || isSpeakingTtsRef.current) return;

          try {
            wakeDetectorRef.current?.stop();
          } catch (_) {}

          stateMachineRef.current?.transitionTo('WAKE_DETECTED');

          const cleanText = (fullTranscript || '')
            .replace(/^hey ion[\s,.]*/i, '')
            .replace(/^hi ion[\s,.]*/i, '')
            .replace(/^hey iron[\s,.]*/i, '')
            .replace(/^hey ian[\s,.]*/i, '')
            .replace(/^ion[\s,.]*/i, '')
            .trim();

          if (cleanText.length > 2) {
            setTranscript(cleanText);
            stateMachineRef.current?.transitionTo('END_OF_TURN');
            addMessage({ role: 'user', content: cleanText });
            handleVoiceResponse(cleanText);
          } else {
            setTimeout(() => {
              stateMachineRef.current?.transitionTo('LISTENING');
              createAndStartRecognition();
              if (mediaStreamRef.current) {
                vadEngineRef.current?.start(mediaStreamRef.current);
              }
            }, 150);
          }
        },
        onError: (err) => {
          console.warn('[ION VOICE] Wake detector error:', err);
          setErrorCode('WAKE_NOT_DETECTED');
        },
      });
    }

    try {
      wakeDetectorRef.current.start();
    } catch (_) {}
  }, [addMessage, createAndStartRecognition, handleVoiceResponse]);

  // Initialize Microphone Stream & VAD Engine
  useEffect(() => {
    if (!SpeechRecognition) {
      setErrorCode('SPEECH_RECOGNITION_UNSUPPORTED');
      setError('Voice recognition is not supported in this browser.');
      setVoiceStatus('offline');
      return;
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      console.log('[ION VOICE] Initializing voice hardware lifecycle...');
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          mediaStreamRef.current = stream;
          setError('');
          setErrorCode(null);
          console.log('[ION VOICE] Microphone permission granted.');
          console.log(`[ION VOICE] Audio stream active: ${stream.active}, Audio tracks: ${stream.getAudioTracks().length}`);

          vadEngineRef.current = new VADEngine({
            speechThreshold: 12,
            silenceTimeoutMs: 1500,
            minSpeechDurationMs: 300,
            onSpeechStart: () => {
              stateMachineRef.current?.onSpeechStart();
            },
            onSpeechEnd: () => {
              if (voiceStatusRef.current === 'user_speaking' || voiceStatusRef.current === 'speech_detected') {
                try {
                  if (recognitionRef.current) {
                    recognitionRef.current.stop();
                  }
                } catch (_) {}
              }
            },
            onDiagnostics: (info) => {
              setVadInfo(info);
            },
          });

          if (handsFreeEnabled) {
            startWakeListening();
          }
        })
        .catch((err) => {
          console.error('[ION VOICE] Microphone permission error:', err);
          setErrorCode('MIC_PERMISSION_DENIED');
          setError('Microphone permission denied or device not accessible. Please grant mic access.');
          setVoiceStatus('offline');
        });
    }

    return () => {
      stopAllAudioResources();
    };
  }, [handsFreeEnabled, startWakeListening, setVoiceStatus, stopAllAudioResources]);

  const startManualListening = async () => {
    setError('');
    setErrorCode(null);
    isFinalizingRef.current = false;

    if (!mediaStreamRef.current && navigator.mediaDevices?.getUserMedia) {
      try {
        mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (err: any) {
        setErrorCode('MIC_PERMISSION_DENIED');
        setError('Microphone permission required. Click "Allow" in browser pop-up.');
        setVoiceStatus('offline');
        return;
      }
    }

    try {
      wakeDetectorRef.current?.stop();
    } catch (_) {}

    stateMachineRef.current?.transitionTo('LISTENING');
    createAndStartRecognition();

    if (mediaStreamRef.current) {
      vadEngineRef.current?.start(mediaStreamRef.current);
    }
  };

  const runVoiceSimulationTest = async (testQuery = "Hey ION, what can you do?") => {
    setError('');
    setErrorCode(null);
    isFinalizingRef.current = false;
    stateMachineRef.current?.transitionTo('WAKE_DETECTED');
    setTranscript(testQuery);

    setTimeout(() => {
      stateMachineRef.current?.transitionTo('LISTENING');
      setTimeout(() => {
        stateMachineRef.current?.transitionTo('USER_SPEAKING');
        setTimeout(() => {
          stateMachineRef.current?.transitionTo('END_OF_TURN');
          addMessage({ role: 'user', content: testQuery });
          handleVoiceResponse(testQuery);
        }, 400);
      }, 300);
    }, 300);
  };

  const toggleHandsFree = () => {
    const nextState = !handsFreeEnabled;
    setHandsFreeEnabled(nextState);
    setError('');
    setErrorCode(null);

    if (nextState) {
      startWakeListening();
    } else {
      stopAllAudioResources();
      stateMachineRef.current?.stop();
    }
  };

  const status = statusMap[voiceStatus] || statusMap['idle'];

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/75 p-6 shadow-futuristic">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">ION Hands-Free Voice</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Ion Audio Hub</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDiagnostics(!showDiagnostics)}
            className="flex items-center gap-1.5 rounded-full border border-white/10 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-300 hover:text-white transition"
          >
            <HiOutlineTerminal size={14} className="text-cyan-400" />
            <span>Diagnostics</span>
          </button>
          <span className={`rounded-full px-4 py-2 text-xs font-semibold tracking-[0.15em] ${status.color}`}>
            {status.label}
          </span>
        </div>
      </div>

      {showDiagnostics && vadInfo && (
        <div className="mt-4 rounded-2xl border border-cyan-500/30 bg-slate-950/90 p-4 text-xs font-mono text-cyan-200">
          <p className="font-bold text-cyan-300 uppercase tracking-wider mb-2">[ION VAD TELEMETRY]</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div>micActive: <span className={vadInfo.micActive ? 'text-emerald-400 font-bold' : 'text-rose-400'}>{String(vadInfo.micActive)}</span></div>
            <div>audioContext: <span className="text-white">{vadInfo.audioContextState}</span></div>
            <div>inputLevel: <span className="text-brand-300 font-bold">{vadInfo.inputLevel}</span></div>
            <div>noiseFloor: <span className="text-amber-300">{vadInfo.noiseFloor}</span></div>
            <div>threshold: <span className="text-cyan-300">{vadInfo.threshold}</span></div>
            <div>speechDetected: <span className={vadInfo.speechDetected ? 'text-emerald-400 font-bold' : 'text-slate-400'}>{String(vadInfo.speechDetected)}</span></div>
            <div>voiceState: <span className="text-purple-300 font-bold">{vadInfo.currentVoiceState}</span></div>
            <div>errorCode: <span className="text-rose-300">{errorCode || 'NONE'}</span></div>
          </div>
        </div>
      )}

      <div className="mt-8 grid gap-6 md:grid-cols-[1fr_auto]">
        <div className="flex flex-col sm:flex-row flex-wrap gap-4">
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
              {handsFreeEnabled ? 'Hands-Free ("Hey Ion")' : 'Enable Hands-Free'}
            </span>
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={startManualListening}
            className="group relative inline-flex items-center justify-center rounded-[1.75rem] border border-cyan-400/30 bg-cyan-500/20 px-6 py-5 font-semibold text-cyan-200 hover:bg-cyan-500/30 transition"
          >
            <HiOutlineMicrophone size={22} className="text-cyan-400 animate-pulse" />
            <span className="ml-3">Tap to Speak Now</span>
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={() => runVoiceSimulationTest()}
            className="group relative inline-flex items-center justify-center rounded-[1.75rem] border border-indigo-400/30 bg-indigo-500/20 px-6 py-5 font-semibold text-indigo-200 hover:bg-indigo-500/30 transition"
          >
            <HiOutlineVolumeUp size={22} className="text-indigo-400 animate-bounce" />
            <span className="ml-3">Run Voice Pipeline Test</span>
          </motion.button>
        </div>

        <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/80 p-5">
          <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-cyan-400 via-brand-500 to-violet-400 opacity-40" />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Live Voice Turn</p>
              <p className="mt-2 text-base text-slate-200">Say "Hey Ion" or click "Tap to Speak Now"</p>
            </div>
            <HiOutlineVolumeUp size={26} className="text-cyan-300" />
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-300 min-h-[120px]">
            {transcript || (handsFreeEnabled ? 'Listening for "Hey Ion"...' : 'Activate Hands-Free Mode above.')}
          </div>
          
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Quick Sample Voice Prompts:</span>
            <button
              onClick={() => runVoiceSimulationTest("What can you do?")}
              className="rounded-xl border border-white/10 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-300 hover:border-cyan-400/50 hover:text-white transition"
            >
              🎤 "What can you do?"
            </button>
            <button
              onClick={() => runVoiceSimulationTest("Tell me a short joke")}
              className="rounded-xl border border-white/10 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-300 hover:border-cyan-400/50 hover:text-white transition"
            >
              🎤 "Tell me a short joke"
            </button>
            <button
              onClick={() => runVoiceSimulationTest("Tell me a fact about space")}
              className="rounded-xl border border-white/10 bg-slate-800/80 px-3 py-1.5 text-xs text-slate-300 hover:border-cyan-400/50 hover:text-white transition"
            >
              🎤 "Fact about space"
            </button>
          </div>

          {error && (
            <div className="mt-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4">
              <p className="text-sm font-semibold text-rose-300">
                {errorCode ? `[${errorCode}] ` : ''}{error}
              </p>
              <button
                onClick={() => startWakeListening()}
                className="mt-2 rounded-xl bg-rose-500/25 px-4 py-2 text-xs font-semibold text-rose-200 hover:bg-rose-500/40 transition border border-rose-400/30"
              >
                Retry / Grant Mic Access
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
