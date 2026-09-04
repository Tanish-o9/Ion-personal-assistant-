export interface WakeWordDetectorOptions {
  wakePhrase?: string;
  phoneticVariants?: string[];
  onWakeWordDetected?: (fullTranscript?: string) => void;
  onError?: (err: string) => void;
}

export class WakeWordDetectorClient {
  private recognition: any = null;
  private primaryWakePhrase: string;
  private phoneticVariants: string[];
  private acceptedPhrases: string[];
  private isListening: boolean = false;
  private onWakeWordDetected?: (fullTranscript?: string) => void;
  private onError?: (err: string) => void;

  constructor(options: WakeWordDetectorOptions = {}) {
    this.primaryWakePhrase = (options.wakePhrase || 'hey ion').toLowerCase().trim();
    const defaultPhonetics = ['hey ion', 'hi ion', 'hey iron', 'hey ian', 'hey eon', 'hey eye on', 'hey i on'];
    const suppliedVariants = options.phoneticVariants && options.phoneticVariants.length > 0 ? options.phoneticVariants : defaultPhonetics;
    this.phoneticVariants = suppliedVariants.map(v => v.toLowerCase().trim());
    this.acceptedPhrases = Array.from(new Set([this.primaryWakePhrase, ...this.phoneticVariants]));
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

    // Clean up previous instance cleanly
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (_) {}
      this.recognition = null;
    }

    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    this.recognition = new SpeechRec();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = typeof navigator !== 'undefined' && navigator.language ? navigator.language : 'en-US';

    this.recognition.onresult = (event: any) => {
      for (let i = 0; i < event.results.length; i++) {
        const rawTranscript = event.results[i][0]?.transcript || '';
        const cleanTranscript = rawTranscript
          .toLowerCase()
          .replace(/[^a-z0-9\s]/g, ' ')
          .replace(/\s+/g, ' ')
          .trim();

        if (cleanTranscript.length >= 2) {
          if (this.onWakeWordDetected) {
            this.onWakeWordDetected(rawTranscript);
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
      if (this.isListening) {
        setTimeout(() => {
          if (this.isListening) {
            this.start(); // Re-create a fresh SpeechRecognition instance on auto-end
          }
        }, 300);
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
        this.recognition.abort();
      } catch (_) {}
      this.recognition = null;
    }
  }
}
