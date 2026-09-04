export interface WakeWordDetectorOptions {
  wakePhrase?: string;
  onWakeWordDetected?: () => void;
  onError?: (err: string) => void;
}

export class WakeWordDetectorClient {
  private recognition: any = null;
  private wakePhrase: string;
  private isListening: boolean = false;
  private onWakeWordDetected?: () => void;
  private onError?: (err: string) => void;

  constructor(options: WakeWordDetectorOptions = {}) {
    this.wakePhrase = (options.wakePhrase || 'hey ion').toLowerCase();
    this.onWakeWordDetected = options.onWakeWordDetected;
    this.onError = options.onError;
  }

  public isSupported(): boolean {
    if (typeof window === 'undefined') return false;
    return !!((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
  }

  public start(): void {
    if (!this.isSupported()) {
      if (this.onError) this.onError('Browser speech recognition is not supported.');
      return;
    }

    if (this.isListening) return;

    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    this.recognition = new SpeechRec();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = (event.results[i][0]?.transcript || '').toLowerCase().strip?.() || event.results[i][0]?.transcript.toLowerCase().trim();
        if (
          transcript.includes('hey ion') ||
          transcript.includes('hey iron') ||
          transcript.includes('hey ian')
        ) {
          if (this.onWakeWordDetected) {
            this.onWakeWordDetected();
          }
          break;
        }
      }
    };

    this.recognition.onerror = (evt: any) => {
      if (evt.error === 'no-speech' || evt.error === 'aborted') return;
      if (this.onError) this.onError(evt.error || 'Wake word detector error.');
    };

    this.recognition.onend = () => {
      // Auto-restart if listening mode is still active
      if (this.isListening) {
        try {
          this.recognition?.start();
        } catch (_) {}
      }
    };

    try {
      this.isListening = true;
      this.recognition.start();
    } catch (err: any) {
      this.isListening = false;
      if (this.onError) this.onError(err.message || 'Failed to start wake word detector.');
    }
  }

  public stop(): void {
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (_) {}
      this.recognition = null;
    }
  }
}
