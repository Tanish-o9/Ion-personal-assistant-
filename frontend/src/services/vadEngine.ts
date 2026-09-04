export interface VADDiagnostics {
  micActive: boolean;
  audioContextState: string;
  inputLevel: number;
  noiseFloor: number;
  threshold: number;
  speechDetected: boolean;
  silenceDurationMs: number;
  currentVoiceState: string;
}

export interface VADConfig {
  fftSize?: number;
  speechThreshold?: number; // Minimum delta above noise floor
  silenceTimeoutMs?: number;
  minSpeechDurationMs?: number;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onVolumeChange?: (volume: number) => void;
  onDiagnostics?: (info: VADDiagnostics) => void;
}

export class VADEngine {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneStream: MediaStream | null = null;
  private mediaStreamSource: MediaStreamAudioSourceNode | null = null;
  private animFrameId: number | null = null;

  private isSpeaking: boolean = false;
  private speechStartTime: number = 0;
  private lastSpeechTime: number = 0;
  private silenceTimer: any = null;

  private speechThreshold: number;
  private noiseFloor: number = 5;
  private silenceTimeoutMs: number;
  private minSpeechDurationMs: number;

  private onSpeechStart?: () => void;
  private onSpeechEnd?: () => void;
  private onVolumeChange?: (volume: number) => void;
  private onDiagnostics?: (info: VADDiagnostics) => void;

  constructor(config: VADConfig = {}) {
    this.speechThreshold = config.speechThreshold ?? 12;
    this.silenceTimeoutMs = config.silenceTimeoutMs ?? 1500;
    this.minSpeechDurationMs = config.minSpeechDurationMs ?? 300;

    this.onSpeechStart = config.onSpeechStart;
    this.onSpeechEnd = config.onSpeechEnd;
    this.onVolumeChange = config.onVolumeChange;
    this.onDiagnostics = config.onDiagnostics;
  }

  public async start(stream: MediaStream): Promise<void> {
    this.stop();
    this.microphoneStream = stream;

    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) {
      console.warn('[ION VOICE] AudioContext is unsupported in this browser.');
      return;
    }

    try {
      console.log('[ION VOICE] Microphone requested & stream attached to VADEngine');
      console.log(`[ION VOICE] Audio stream active: ${stream.active}, Audio tracks: ${stream.getAudioTracks().length}`);

      this.audioContext = new AudioCtx();
      if (this.audioContext.state === 'suspended') {
        console.log('[ION VOICE] AudioContext state: suspended → attempting resume()');
        await this.audioContext.resume().catch((err) => {
          console.warn('[ION VOICE] AudioContext resume failed:', err);
        });
      }
      console.log(`[ION VOICE] AudioContext state: ${this.audioContext.state}`);

      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 512;
      this.analyser.smoothingTimeConstant = 0.4;

      this.mediaStreamSource = this.audioContext.createMediaStreamSource(stream);
      this.mediaStreamSource.connect(this.analyser);

      this.processAudio();
    } catch (err: any) {
      console.error('[ION VOICE] Error starting AudioContext / AnalyserNode:', err);
    }
  }

  private processAudio = () => {
    if (!this.analyser) return;

    if (this.audioContext && this.audioContext.state === 'suspended') {
      this.audioContext.resume().catch(() => {});
    }

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i];
    }
    const currentVolume = sum / bufferLength;

    // Dynamically update noise floor during quiet periods
    if (currentVolume < this.noiseFloor + 5) {
      this.noiseFloor = this.noiseFloor * 0.95 + currentVolume * 0.05;
    }

    const dynamicThreshold = Math.max(10, Math.round(this.noiseFloor + this.speechThreshold));

    if (this.onVolumeChange) {
      this.onVolumeChange(currentVolume);
    }

    const speechDetected = currentVolume > dynamicThreshold;
    const now = Date.now();

    if (speechDetected) {
      this.lastSpeechTime = now;
      if (!this.isSpeaking) {
        this.isSpeaking = true;
        this.speechStartTime = now;
        console.log(`[ION VAD] inputLevel=${Math.round(currentVolume)} noiseFloor=${Math.round(this.noiseFloor)} threshold=${dynamicThreshold} speech=true state=USER_SPEAKING`);
        if (this.onSpeechStart) {
          this.onSpeechStart();
        }
      }
      this.clearSilenceTimer();
    } else {
      if (this.isSpeaking) {
        if (!this.silenceTimer) {
          this.silenceTimer = setTimeout(() => {
            const speechDuration = Date.now() - this.speechStartTime;
            if (speechDuration >= this.minSpeechDurationMs) {
              this.isSpeaking = false;
              console.log(`[ION VAD] inputLevel=${Math.round(currentVolume)} noiseFloor=${Math.round(this.noiseFloor)} threshold=${dynamicThreshold} speech=false state=END_OF_TURN`);
              if (this.onSpeechEnd) {
                this.onSpeechEnd();
              }
            } else {
              this.isSpeaking = false;
            }
            this.clearSilenceTimer();
          }, this.silenceTimeoutMs);
        }
      }
    }

    if (this.onDiagnostics) {
      const silenceDurationMs = this.isSpeaking ? 0 : now - (this.lastSpeechTime || now);
      const voiceState = !this.microphoneStream || !this.microphoneStream.active
        ? 'NO_AUDIO'
        : speechDetected
        ? 'USER_SPEAKING'
        : this.isSpeaking
        ? 'SPEECH_DETECTED'
        : 'SILENCE';

      this.onDiagnostics({
        micActive: !!(this.microphoneStream && this.microphoneStream.active),
        audioContextState: this.audioContext ? this.audioContext.state : 'closed',
        inputLevel: Math.round(currentVolume),
        noiseFloor: Math.round(this.noiseFloor),
        threshold: dynamicThreshold,
        speechDetected,
        silenceDurationMs,
        currentVoiceState: voiceState,
      });
    }

    this.animFrameId = requestAnimationFrame(this.processAudio);
  };

  private clearSilenceTimer(): void {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
  }

  public stop(): void {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }

    this.clearSilenceTimer();
    this.isSpeaking = false;

    if (this.mediaStreamSource) {
      try {
        this.mediaStreamSource.disconnect();
      } catch (_) {}
      this.mediaStreamSource = null;
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      try {
        this.audioContext.close();
      } catch (_) {}
      this.audioContext = null;
    }

    this.analyser = null;
    this.microphoneStream = null;
  }
}
