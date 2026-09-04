import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { HiOutlineClipboard, HiOutlineSparkles } from 'react-icons/hi';
import { motion } from 'framer-motion';

import { useWebSocket, MultimodalPayloadFile } from '../../hooks/useWebSocket';
import ActivityPanel from '../activity/ActivityPanel';
import ToolExecutionPanel from '../tools/ToolExecutionPanel';
import TaskPanel from '../task/TaskPanel';
import AdaptivePlanPanel from './AdaptivePlanPanel';
import VoiceControls from '../voice/VoiceControls';
import FileUpload from '../upload/FileUpload';
import SourcesPanel from '../sources/SourcesPanel';
import JobsPanel from '../jobs/JobsPanel';
import AutomationPanel from '../automation/AutomationPanel';
import { postChat, fetchSessionMessages } from '../../services/api';

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatWindowProps {
  sessionId: string;
  userId: string;
  onNewSession?: () => void;
}

export default function ChatWindow({ sessionId, userId, onNewSession }: ChatWindowProps) {
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [attachedFile, setAttachedFile] = useState<MultimodalPayloadFile | null>(null);
  const [copySuccess, setCopySuccess] = useState('');
  const [isHttpLoading, setIsHttpLoading] = useState(false);

  const scrollRef = useRef<HTMLDivElement | null>(null);

  const {
    isConnected,
    activityEvents,
    toolExecutions,
    taskPlan,
    researchSources,
    transcript,
    latestAudioBase64,
    finalAnswer,
    sendTextMessage,
    sendVoiceMessage,
    sendCancel,
  } = useWebSocket(sessionId, userId);

  useEffect(() => {
    if (sessionId) {
      fetchSessionMessages(sessionId)
        .then((data: any[]) => {
          if (Array.isArray(data)) {
            setMessages(
              data.map((m) => ({
                id: m.id,
                role: m.role as 'user' | 'assistant',
                content: m.content,
                timestamp: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              }))
            );
          }
        })
        .catch(() => {});
    }
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, finalAnswer]);

  useEffect(() => {
    if (finalAnswer) {
      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === finalAnswer) {
          return prev;
        }
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: finalAnswer,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ];
      });
      setIsHttpLoading(false);
    }
  }, [finalAnswer]);

  const copyLatest = async () => {
    const latest = messages[messages.length - 1];
    if (!latest) return;
    await navigator.clipboard.writeText(latest.content);
    setCopySuccess('Copied to clipboard');
    setTimeout(() => setCopySuccess(''), 1800);
  };

  const handleSend = async () => {
    if (!inputValue.trim() && !attachedFile) return;

    const userText = inputValue.trim() || 'Process attached file';
    const filesToSend = attachedFile ? [attachedFile] : undefined;

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: userText + (attachedFile ? ` [File: ${attachedFile.filename}]` : ''),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);

    setInputValue('');
    setAttachedFile(null);

    if (isConnected) {
      sendTextMessage(userText, filesToSend);
    } else {
      setIsHttpLoading(true);
      try {
        const res = await postChat({
          session_id: sessionId,
          text: userText,
          files: filesToSend,
        });

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: res.response,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } catch (err: any) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Error: ${err?.message || 'Failed to communicate with ION backend'}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } finally {
        setIsHttpLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceTranscript = (voiceText: string) => {
    if (!voiceText) return;
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: voiceText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const handleVoiceResponse = (voiceResponseText: string) => {
    if (!voiceResponseText) return;
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: voiceResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="grid gap-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Control Center</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">ION Multimodal Interface</h2>
            <p className="mt-1 text-xs font-mono text-brand-300">Session ID: {sessionId}</p>
          </div>

          <div className="flex items-center gap-3">
            {onNewSession && (
              <button
                onClick={onNewSession}
                className="rounded-3xl border border-white/10 bg-slate-950 px-4 py-2.5 text-xs text-slate-300 transition hover:border-brand-400 hover:text-white"
              >
                + New Session
              </button>
            )}
            <button
              onClick={copyLatest}
              className="inline-flex items-center gap-2 rounded-3xl bg-brand-500/15 px-4 py-2.5 text-xs text-brand-200 transition hover:bg-brand-500/25"
            >
              <HiOutlineClipboard size={16} /> Copy latest
            </button>
          </div>
        </div>
        {copySuccess && <p className="mt-2 text-xs text-emerald-300">{copySuccess}</p>}
      </div>

      <JobsPanel />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="flex flex-col gap-6">
          <div ref={scrollRef} className="max-h-[550px] space-y-4 overflow-y-auto pr-2 pb-2">
            {messages.length > 0 ? (
              messages.map((m) => (
                <div
                  key={m.id}
                  className={`rounded-3xl border ${
                    m.role === 'assistant' ? 'border-slate-800 bg-slate-900/95' : 'border-slate-700 bg-slate-950/90'
                  } p-5 shadow-sm`}
                >
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <span className="text-xs uppercase tracking-[0.25em] text-slate-500">
                      {m.role === 'assistant' ? 'Ion' : 'You'}
                    </span>
                    <span className="text-[11px] text-slate-500">{m.timestamp}</span>
                  </div>
                  <div className="prose prose-invert max-w-none text-sm leading-7">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                </div>
              ))
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-center rounded-[2rem] border border-dashed border-slate-700 bg-slate-950/60 p-16 text-center text-slate-400"
              >
                <div>
                  <HiOutlineSparkles size={28} className="mx-auto mb-4 text-brand-300" />
                  <p className="text-sm">Start a conversation with ION via text, voice, images, or uploaded documents.</p>
                </div>
              </motion.div>
            )}

            {isHttpLoading && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-4 text-xs text-slate-400 italic animate-pulse">
                ION is reasoning...
              </div>
            )}
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-4 shadow-futuristic">
            <div className="mb-3">
              <FileUpload onFileSelected={setAttachedFile} />
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={2}
                className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-100 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10 resize-none"
                placeholder="Ask ION anything (Enter to send, Shift+Enter for new line)..."
              />
              <button
                onClick={handleSend}
                disabled={isHttpLoading}
                className="rounded-2xl bg-brand-500 px-6 py-4 text-sm font-semibold text-slate-950 transition hover:bg-brand-400 disabled:opacity-60"
              >
                {isHttpLoading ? 'Processing...' : 'Send'}
              </button>
            </div>
          </div>

          <VoiceControls
            sessionId={sessionId}
            userId={userId}
            transcript={transcript}
            latestAudioBase64={latestAudioBase64}
            onTranscriptReceived={handleVoiceTranscript}
            onResponseReceived={handleVoiceResponse}
            onCancel={sendCancel}
          />
        </div>

        <div className="space-y-6">
          {taskPlan && <AdaptivePlanPanel plan={taskPlan} />}
          <AutomationPanel />
          <ActivityPanel events={activityEvents} isConnected={isConnected} />
          <ToolExecutionPanel tools={toolExecutions} />
          <TaskPanel plan={taskPlan} />
          <SourcesPanel sources={researchSources} />
        </div>
      </div>
    </div>
  );
}
