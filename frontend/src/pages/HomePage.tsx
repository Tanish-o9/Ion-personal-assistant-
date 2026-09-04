import { useState, useEffect, useRef } from 'react';
import VoiceCore from '../components/voice/VoiceCore';
import VoicePanel from '../components/voice/VoicePanel';
import ChatWindow from '../components/chat/ChatWindow';
import ActivityPanel from '../components/activity/ActivityPanel';
import JobsPanel from '../components/jobs/JobsPanel';
import AutomationPanel from '../components/automation/AutomationPanel';
import { useWebSocket } from '../hooks/useWebSocket';

interface HomePageProps {
  sessionId: string;
  userId: string;
  onNewSession: () => void;
}

export default function HomePage({ sessionId, userId, onNewSession }: HomePageProps) {
  const {
    isConnected,
    activityEvents,
    transcript,
    finalAnswer,
    sendCancel,
  } = useWebSocket(sessionId, userId);

  return (
    <div className="w-full space-y-6">
      {/* Voice-First 70% / 30% Main Control Center Grid */}
      <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr] xl:grid-cols-[1.8fr_1fr]">
        {/* Left / Hero Voice Core Column (~70%) */}
        <div className="space-y-6">
          <VoiceCore
            transcript={transcript}
            response={finalAnswer}
            isConnected={isConnected}
            onCancel={sendCancel}
          />

          <VoicePanel />

          <div className="grid gap-6 md:grid-cols-2">
            <JobsPanel />
            <AutomationPanel />
          </div>
        </div>

        {/* Right / Secondary Conversation & Telemetry Column (~30%) */}
        <div className="space-y-6">
          <ChatWindow sessionId={sessionId} userId={userId} onNewSession={onNewSession} />
          <ActivityPanel events={activityEvents} isConnected={isConnected} />
        </div>
      </div>
    </div>
  );
}
