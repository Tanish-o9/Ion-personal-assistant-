import { useContext } from 'react';
import { useMutation } from '@tanstack/react-query';
import { AssistantContext } from '../contexts/AssistantContext';
import { postChat } from '../services/chatService';

export function useChat() {
  const { chatHistory, addMessage, currentModel, setVoiceStatus } = useContext(AssistantContext);

  const mutation = useMutation({
    mutationFn: postChat,
    onSuccess: (data) => {
      addMessage({ role: 'assistant', content: data.message.content });
      setVoiceStatus('speaking');
      window.setTimeout(() => setVoiceStatus('idle'), 1200);
    },
    onError: () => {
      setVoiceStatus('offline');
    },
  });

  const sendMessage = async (question: string) => {
    addMessage({ role: 'user', content: question });
    setVoiceStatus('processing');
    await mutation.mutateAsync({ question, context: chatHistory, model: currentModel });
  };

  return {
    ...mutation,
    sendMessage,
  };
}
