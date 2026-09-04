export interface VADConfig {
  fftSize?: number;
  speechThreshold?: number; // Volume threshold (0-255)
  silenceTimeoutMs?: number;
  minSpeechDurationMs?: number;
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onVolumeChange?: (volume: number) => void;
}

export class VADEngine {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphoneStream: MediaStream | null = null;
  private mediaStreamSource: MediaStreamAudioSourceNode | null = null;
  private animFrameId: number | null = null;

  private isSpeaking: boolean = false;
  private speechStartTime: number = 0;
  private silenceTimer: any = null;

  private speechThreshold: number;
  private silenceTimeoutMs: number;
  private minSpeechDurationMs: number;

  private onSpeechStart?: () => void;
  private onSpeechEnd?: () => void;
  private onVolumeChange?: (volume: number) => void;

  constructor(config: VADConfig = {}) {
    this.speechThreshold = config.speechThreshold ?? 15;
    this.silenceTimeoutMs = config.silenceTimeoutMs ?? 1500;
    this.minSpeechDurationMs = config.minSpeechDurationMs ?? 300;

    this.onSpeechStart = config.onSpeechStart;
    this.onSpeechEnd = config.onSpeechEnd;
    this.onVolumeChange = config.onVolumeChange;
  }

  public async start(stream: MediaStream): Promise<void> {
    this.stop();
    this.microphoneStream = stream;

    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;

    this.audioContext = new AudioCtx();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 512;
    this.analyser.smoothingTimeConstant = 0.4;

    this.mediaStreamSource = this.audioContext.createMediaStreamSource(stream);
    this.mediaStreamSource.connect(this.analyser);

    this.processAudio();
  }

  private processAudio = () => {
    if (!this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i];
    }
    const averageVolume = sum / bufferLength;

    if (this.onVolumeChange) {
      this.onVolumeChange(averageVolume);
    }

    if (averageVolume > this.speechThreshold) {
      if (!this.isSpeaking) {
        this.isSpeaking = true;
        this.speechStartTime = Date.now();
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
