import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { HiOutlineClipboard, HiOutlineSparkles } from 'react-icons/hi';
import { motion } from 'framer-motion';

import { useWebSocket, MultimodalPayloadFile } from '../../hooks/useWebSocket';
import ToolExecutionPanel from '../tools/ToolExecutionPanel';
import TaskPanel from '../task/TaskPanel';
import AdaptivePlanPanel from './AdaptivePlanPanel';
import FileUpload from '../upload/FileUpload';
import SourcesPanel from '../sources/SourcesPanel';
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
    toolExecutions,
    taskPlan,
    researchSources,
    finalAnswer,
    sendTextMessage,
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
    setCopySuccess('Copied');
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

  return (
    <div className="flex flex-col gap-4 rounded-[2rem] border border-white/10 bg-slate-900/80 p-5 shadow-futuristic">
      {/* Side Panel Header */}
      <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-3">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Secondary Interaction</p>
          <h3 className="text-base font-bold text-white">Conversation History</h3>
        </div>
        <div className="flex items-center gap-2">
          {onNewSession && (
            <button
              onClick={onNewSession}
              className="rounded-2xl border border-white/10 bg-slate-950 px-3 py-1.5 text-xs text-slate-300 transition hover:border-brand-400 hover:text-white"
            >
              + New Session
            </button>
          )}
          <button
            onClick={copyLatest}
            className="rounded-2xl bg-brand-500/15 p-2 text-brand-300 transition hover:bg-brand-500/25"
            title="Copy latest response"
          >
            <HiOutlineClipboard size={16} />
          </button>
        </div>
      </div>
      {copySuccess && <p className="text-xs text-emerald-300">{copySuccess}</p>}

      {/* Messages Scroll Area */}
      <div ref={scrollRef} className="max-h-[380px] space-y-3 overflow-y-auto pr-1">
        {messages.length > 0 ? (
          messages.map((m) => (
            <div
              key={m.id}
              className={`rounded-2xl border ${
                m.role === 'assistant' ? 'border-slate-800 bg-slate-950/90' : 'border-slate-700 bg-slate-900/90'
              } p-4 text-xs shadow-sm`}
            >
              <div className="mb-1 flex items-center justify-between">
                <span className="font-semibold uppercase tracking-wider text-slate-400">
                  {m.role === 'assistant' ? 'Ion' : 'You'}
                </span>
                <span className="text-[10px] text-slate-500">{m.timestamp}</span>
              </div>
              <div className="prose prose-invert max-w-none text-xs leading-relaxed">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
              </div>
            </div>
          ))
        ) : (
          <div className="py-8 text-center text-xs text-slate-500 italic">
            No text messages yet. Say "Hey Ion" to start.
          </div>
        )}

        {isHttpLoading && (
          <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-3 text-xs text-slate-400 italic animate-pulse">
            ION is thinking...
          </div>
        )}
      </div>

      {/* Text Fallback Input */}
      <div className="rounded-2xl border border-white/10 bg-slate-950/90 p-3 space-y-2">
        <FileUpload onFileSelected={setAttachedFile} />
        <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            className="min-w-0 flex-1 rounded-xl border border-white/10 bg-slate-900/90 p-2.5 text-xs text-slate-100 outline-none transition focus:border-brand-400 resize-none"
            placeholder="Type text command as fallback..."
          />
          <button
            onClick={handleSend}
            disabled={isHttpLoading}
            className="rounded-xl bg-brand-500 px-4 py-2 text-xs font-semibold text-slate-950 transition hover:bg-brand-400 disabled:opacity-60"
          >
            Send
          </button>
        </div>
      </div>

      {/* Secondary Panels */}
      {taskPlan && <AdaptivePlanPanel plan={taskPlan} />}
      {toolExecutions.length > 0 && <ToolExecutionPanel tools={toolExecutions} />}
      {taskPlan && <TaskPanel plan={taskPlan} />}
      {researchSources.length > 0 && <SourcesPanel sources={researchSources} />}
    </div>
  );
}
