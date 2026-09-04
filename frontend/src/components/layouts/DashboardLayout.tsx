import { ReactNode, useState } from 'react';
import Sidebar from '../sidebar/Sidebar';
import { motion } from 'framer-motion';

interface DashboardLayoutProps {
  children: ReactNode;
  onNewSession?: () => void;
  currentSessionId?: string;
  onSelectSession?: (sessionId: string) => void;
}

export default function DashboardLayout({
  children,
  onNewSession,
  currentSessionId,
  onSelectSession,
}: DashboardLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-radial-grid opacity-20" />
        <div className="relative mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            className={`hidden shrink-0 lg:block ${collapsed ? 'w-24' : 'w-80'}`}
          >
            <Sidebar
              collapsed={collapsed}
              setCollapsed={setCollapsed}
              onNewSession={onNewSession}
              currentSessionId={currentSessionId}
              onSelectSession={onSelectSession}
            />
          </motion.div>

          <motion.main
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.08 }}
            className="flex-1 min-w-0"
          >
            {children}
          </motion.main>
        </div>
      </div>
    </div>
  );
}
