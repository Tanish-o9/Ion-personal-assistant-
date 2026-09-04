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

    if (this.isListening) return;

    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    this.recognition = new SpeechRec();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    const WAKE_PATTERN = /(hey|hi|hello|aion)\b[\s\w]*(ion|iron|ian|eon|eye|john|neon|ai|one)\b/i;

    this.recognition.onresult = (event: any) => {
      for (let i = 0; i < event.results.length; i++) {
        const rawTranscript = event.results[i][0]?.transcript || '';
        const cleanTranscript = rawTranscript
          .toLowerCase()
          .replace(/[^a-z0-9\s]/g, ' ')
          .replace(/\s+/g, ' ')
          .trim();

        const matchesAccepted = this.acceptedPhrases.some(phrase => cleanTranscript.includes(phrase));
        const matchesPattern = WAKE_PATTERN.test(cleanTranscript) || cleanTranscript.includes('hey ion') || cleanTranscript.includes('hi ion');

        if (matchesAccepted || matchesPattern) {
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
      // Auto-restart with delay if listening mode is still active
      if (this.isListening) {
        setTimeout(() => {
          if (this.isListening && this.recognition) {
            try {
              this.recognition.start();
            } catch (_) {}
          }
        }, 500);
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
