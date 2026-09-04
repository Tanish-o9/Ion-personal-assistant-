import ChatWindow from '../components/chat/ChatWindow';

interface HomePageProps {
  sessionId: string;
  userId: string;
  onNewSession: () => void;
}

export default function HomePage({ sessionId, userId, onNewSession }: HomePageProps) {
  return (
    <div className="w-full">
      <ChatWindow sessionId={sessionId} userId={userId} onNewSession={onNewSession} />
    </div>
  );
}
