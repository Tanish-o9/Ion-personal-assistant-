import { useState, useRef, useEffect } from 'react';
import { HiOutlineMicrophone, HiOutlineStop, HiOutlineVolumeUp, HiOutlineX } from 'react-icons/hi';
import { postVoice } from '../../services/api';

interface VoiceControlsProps {
  sessionId: string;
  userId: string;
  transcript: string;
  latestAudioBase64: string | null;
  onTranscriptReceived?: (text: string) => void;
  onResponseReceived?: (text: string) => void;
  onCancel?: () => void;
}

export default function VoiceControls({
  sessionId,
  userId,
  transcript,
  latestAudioBase64,
  onTranscriptReceived,
  onResponseReceived,
  onCancel,
}: VoiceControlsProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Play audio response when base64 payload updates
  useEffect(() => {
    if (latestAudioBase64) {
      try {
        const audioUrl = `data:audio/wav;base64,${latestAudioBase64}`;
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          audioRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
        }
      } catch (err) {
        console.error('Audio playback error:', err);
      }
    }
  }, [latestAudioBase64]);

  const startRecording = async () => {
    setVoiceError(null);
    audioChunksRef.current = [];

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setVoiceError('Microphone recording is not supported in this browser.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });

        if (audioBlob.size === 0) {
          setIsProcessing(false);
          return;
        }

        const reader = new FileReader();
        reader.onloadend = async () => {
          const resultStr = reader.result as string;
          const base64Data = resultStr.split(',')[1] || '';

          try {
            setIsProcessing(true);
            const voiceRes = await postVoice({
              session_id: sessionId,
              audio_base64: base64Data,
              audio_format: 'wav',
            });

            if (voiceRes.transcript && onTranscriptReceived) {
              onTranscriptReceived(voiceRes.transcript);
            }
            if (voiceRes.response_text && onResponseReceived) {
              onResponseReceived(voiceRes.response_text);
            }

            if (voiceRes.audio_base64 && audioRef.current) {
              audioRef.current.src = `data:audio/wav;base64,${voiceRes.audio_base64}`;
              audioRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
            }
          } catch (err: any) {
            setVoiceError(err?.message || 'Voice pipeline processing failed.');
          } finally {
            setIsProcessing(false);
          }
        };
        reader.readAsDataURL(audioBlob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (err) {
      setVoiceError('Microphone permission denied or device error.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} className="hidden" />

      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Audio System</p>
          <h3 className="text-lg font-semibold text-white">Voice Interaction</h3>
        </div>

        <div className="flex items-center gap-2">
          {onCancel && (
            <button
              onClick={onCancel}
              className="flex items-center gap-1 rounded-full border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs text-rose-300 transition hover:bg-rose-500/20"
            >
              <HiOutlineX size={14} /> Interrupt
            </button>
          )}
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold tracking-wider ${
              isRecording
                ? 'bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/40 animate-pulse'
                : isProcessing
                ? 'bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/40'
                : isPlaying
                ? 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/40'
                : 'bg-slate-800 text-slate-400'
            }`}
          >
            {isRecording
              ? '🔴 Recording...'
              : isProcessing
              ? '⏳ Processing...'
              : isPlaying
              ? '🔊 ION speaking...'
              : '🎤 Ready'}
          </span>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isProcessing}
            className="flex items-center gap-2 rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-brand-400 disabled:opacity-50"
          >
            <HiOutlineMicrophone size={18} /> Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center gap-2 rounded-2xl bg-rose-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-rose-600"
          >
            <HiOutlineStop size={18} /> Stop Recording
          </button>
        )}

        {transcript && (
          <div className="flex-1 rounded-2xl border border-white/10 bg-slate-950/80 p-3 text-xs text-slate-300">
            <span className="text-slate-500 font-semibold">Transcript: </span>
            {transcript}
          </div>
        )}
      </div>

      {voiceError && <p className="mt-3 text-xs text-rose-400">{voiceError}</p>}
    </div>
  );
}
