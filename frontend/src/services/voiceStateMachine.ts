export type VoiceState =
  | 'IDLE'
  | 'WAKE_LISTENING'
  | 'WAKE_DETECTED'
  | 'LISTENING'
  | 'SPEECH_DETECTED'
  | 'USER_SPEAKING'
  | 'END_OF_TURN'
  | 'TRANSCRIBING'
  | 'PROCESSING'
  | 'RESPONDING'
  | 'SPEAKING'
  | 'ERROR'
  | 'INTERRUPTED';

export interface VoiceStateMachineConfig {
  silenceTimeoutMs?: number;
  minSpeechDurationMs?: number;
  maxTurnDurationMs?: number;
  onStateChange?: (newState: VoiceState, prevState: VoiceState) => void;
}

export class VoiceStateMachine {
  private currentState: VoiceState = 'IDLE';
  private silenceTimeoutMs: number;
  private minSpeechDurationMs: number;
  private maxTurnDurationMs: number;
  private onStateChange?: (newState: VoiceState, prevState: VoiceState) => void;

  private turnTimer: any = null;
  private silenceTimer: any = null;
  private speechStartTime: number = 0;

  constructor(config: VoiceStateMachineConfig = {}) {
    this.silenceTimeoutMs = config.silenceTimeoutMs ?? 1500;
    this.minSpeechDurationMs = config.minSpeechDurationMs ?? 300;
    this.maxTurnDurationMs = config.maxTurnDurationMs ?? 30000;
    this.onStateChange = config.onStateChange;
  }

  public getState(): VoiceState {
    return this.currentState;
  }

  public transitionTo(nextState: VoiceState): boolean {
    if (this.currentState === nextState) return false;

    const prevState = this.currentState;
    this.currentState = nextState;

    if (this.onStateChange) {
      this.onStateChange(nextState, prevState);
    }

    // Handle state lifecycle side effects
    if (nextState === 'LISTENING' || nextState === 'SPEECH_DETECTED' || nextState === 'USER_SPEAKING') {
      this.startMaxTurnTimer();
    } else {
      this.clearMaxTurnTimer();
    }

    if (nextState !== 'USER_SPEAKING') {
      this.clearSilenceTimer();
    }

    return true;
  }

  public onSpeechStart(): void {
    if (this.currentState === 'LISTENING' || this.currentState === 'WAKE_DETECTED') {
      this.speechStartTime = Date.now();
      this.transitionTo('SPEECH_DETECTED');
      this.transitionTo('USER_SPEAKING');
    }
  }

  public onSilenceDetected(onEndOfTurnCallback: () => void): void {
    if (this.currentState !== 'USER_SPEAKING') return;

    const speechDuration = Date.now() - this.speechStartTime;
    if (speechDuration < this.minSpeechDurationMs) {
      // Ignore tiny noise clicks
      return;
    }

    this.clearSilenceTimer();
    this.silenceTimer = setTimeout(() => {
      if (this.currentState === 'USER_SPEAKING') {
        this.transitionTo('END_OF_TURN');
        onEndOfTurnCallback();
      }
    }, this.silenceTimeoutMs);
  }

  public resetToWakeListening(): void {
    this.clearAllTimers();
    this.transitionTo('WAKE_LISTENING');
  }

  public stop(): void {
    this.clearAllTimers();
    this.transitionTo('IDLE');
  }

  private startMaxTurnTimer(): void {
    if (this.turnTimer) return;
    this.turnTimer = setTimeout(() => {
      if (
        this.currentState === 'LISTENING' ||
        this.currentState === 'SPEECH_DETECTED' ||
        this.currentState === 'USER_SPEAKING'
      ) {
        this.transitionTo('END_OF_TURN');
      }
    }, this.maxTurnDurationMs);
  }

  private clearMaxTurnTimer(): void {
    if (this.turnTimer) {
      clearTimeout(this.turnTimer);
      this.turnTimer = null;
    }
  }

  private clearSilenceTimer(): void {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
  }

  private clearAllTimers(): void {
    this.clearMaxTurnTimer();
    this.clearSilenceTimer();
  }
}
