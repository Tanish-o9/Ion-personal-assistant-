import { useContext, useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  HiOutlineSparkles,
  HiOutlineDocumentText,
  HiOutlineUserCircle,
  HiOutlineClipboardList,
  HiOutlineChevronDoubleLeft,
  HiOutlineChevronDoubleRight,
  HiOutlinePlus,
  HiOutlineLogout,
  HiOutlineChatAlt2,
  HiOutlineChartBar,
} from 'react-icons/hi';
import { AuthContext } from '../../contexts/AuthContext';
import { fetchConversations } from '../../services/api';

interface ConversationItem {
  session_id: string;
  title: string;
  updated_at: string;
}

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
  onNewSession?: () => void;
  currentSessionId?: string;
  onSelectSession?: (sessionId: string) => void;
}

const navItems = [
  { label: 'Chat', path: '/', icon: HiOutlineSparkles },
  { label: 'Tasks', path: '/tasks', icon: HiOutlineClipboardList },
  { label: 'Memory', path: '/memory', icon: HiOutlineDocumentText },
  { label: 'Profile', path: '/profile', icon: HiOutlineUserCircle },
  { label: 'Telemetry', path: '/monitoring', icon: HiOutlineChartBar },
];

export default function Sidebar({
  collapsed,
  setCollapsed,
  onNewSession,
  currentSessionId,
  onSelectSession,
}: SidebarProps) {
  const { user, logout } = useContext(AuthContext);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);

  useEffect(() => {
    if (user) {
      fetchConversations()
        .then((data) => setConversations(data))
        .catch(() => {});
    }
  }, [user, currentSessionId]);

  return (
    <aside className="backdrop-glass rounded-3xl border border-white/10 p-5 shadow-futuristic transition-all duration-300 flex flex-col justify-between">
      <div>
        <div className="mb-6 flex items-center justify-between gap-3 rounded-3xl bg-slate-900/80 p-4 shadow-lg shadow-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-500/10 text-brand-200 ring-1 ring-brand-400/20">
              <HiOutlineSparkles size={22} />
            </div>
            {!collapsed && (
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-400">ION</p>
                <h1 className="text-lg font-semibold text-white">Control Center</h1>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="rounded-2xl border border-white/10 bg-slate-950/85 p-2 text-slate-300 transition hover:border-brand-400 hover:text-brand-200"
          >
            {collapsed ? <HiOutlineChevronDoubleRight size={18} /> : <HiOutlineChevronDoubleLeft size={18} />}
          </button>
        </div>

        {user && !collapsed && (
          <div className="mb-4 rounded-2xl border border-white/10 bg-slate-950/80 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HiOutlineUserCircle size={18} className="text-brand-400" />
              <span className="text-xs font-semibold text-slate-200">{user.username}</span>
            </div>
            <button
              onClick={logout}
              className="text-slate-400 hover:text-rose-400 transition p-1"
              title="Log out"
            >
              <HiOutlineLogout size={16} />
            </button>
          </div>
        )}

        {!collapsed && onNewSession && (
          <button
            onClick={onNewSession}
            className="mb-6 flex w-full items-center justify-center gap-2 rounded-3xl bg-brand-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-brand-500/20 transition hover:bg-brand-400"
          >
            <HiOutlinePlus size={18} /> New Conversation
          </button>
        )}

        <div className="space-y-2 mb-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-medium transition ${
                    isActive ? 'bg-brand-500/15 text-white ring-1 ring-brand-400/30' : 'text-slate-300 hover:bg-slate-900/70'
                  }`
                }
              >
                <Icon size={20} />
                {!collapsed && item.label}
              </NavLink>
            );
          })}
        </div>

        {!collapsed && conversations.length > 0 && (
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.25em] text-slate-500 font-medium mb-3">Recent Chats</p>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {conversations.slice(0, 10).map((c) => (
                <button
                  key={c.session_id}
                  onClick={() => onSelectSession && onSelectSession(c.session_id)}
                  className={`w-full text-left flex items-center gap-2.5 rounded-2xl px-3 py-2 text-xs transition ${
                    currentSessionId === c.session_id
                      ? 'bg-brand-500/20 text-brand-300 font-semibold ring-1 ring-brand-400/30'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  <HiOutlineChatAlt2 size={16} className="shrink-0 text-slate-500" />
                  <span className="truncate">{c.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {!collapsed && (
        <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-4">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Observability</p>
          <div className="mt-3 rounded-2xl bg-slate-950/80 p-3 text-xs text-slate-300 space-y-1">
            <p className="font-semibold text-emerald-400">Telemetry Active</p>
            <p className="text-slate-400 text-[11px]">JSON Logging & Prometheus</p>
          </div>
        </div>
      )}
    </aside>
  );
}
