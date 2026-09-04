import { useState, useCallback, useContext } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Route, Routes, useLocation } from 'react-router-dom';
import DashboardLayout from './components/layouts/DashboardLayout';
import HomePage from './pages/HomePage';
import TasksPage from './pages/TasksPage';
import MemoryPage from './pages/MemoryPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DeveloperPanel from './components/monitoring/DeveloperPanel';
import ReasoningSimulationPage from './pages/ReasoningSimulationPage';
import DevicesPage from './pages/DevicesPage';
import { EnterpriseDashboardPage } from './pages/EnterpriseDashboardPage';
import { AuthContext, AuthProvider } from './contexts/AuthContext';




const pageTransition = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -16 },
};

function MainDashboard() {
  const location = useLocation();
  const { user } = useContext(AuthContext);
  const [sessionId, setSessionId] = useState<string>(() => crypto.randomUUID());
  const userId = user?.id || 'default_user';

  const handleNewSession = useCallback(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  const handleSelectSession = useCallback((selectedSessionId: string) => {
    setSessionId(selectedSessionId);
  }, []);

  return (
    <DashboardLayout
      onNewSession={handleNewSession}
      currentSessionId={sessionId}
      onSelectSession={handleSelectSession}
    >
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route
            path="/"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <HomePage sessionId={sessionId} userId={userId} onNewSession={handleNewSession} />
              </motion.div>
            }
          />
          <Route
            path="/tasks"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <TasksPage sessionId={sessionId} userId={userId} />
              </motion.div>
            }
          />
          <Route
            path="/memory"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <MemoryPage userId={userId} />
              </motion.div>
            }
          />
          <Route
            path="/profile"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <ProfilePage userId={userId} />
              </motion.div>
            }
          />

          <Route
            path="/monitoring"

            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <DeveloperPanel />
              </motion.div>
            }
          />

          <Route
            path="/reasoning-simulation"

            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <ReasoningSimulationPage />
              </motion.div>
            }
          />
          <Route
            path="/devices"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <DevicesPage />
              </motion.div>
            }
          />
          <Route
            path="/enterprise"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.35 }}>
                <EnterpriseDashboardPage />
              </motion.div>
            }
          />
        </Routes>
      </AnimatePresence>
    </DashboardLayout>
  );


}

function AuthenticatedApp() {
  const { isAuthenticated, isLoading } = useContext(AuthContext);
  const [isRegisterView, setIsRegisterView] = useState(false);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400 text-xs font-mono">
        Authenticating session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return isRegisterView ? (
      <RegisterPage onSwitchToLogin={() => setIsRegisterView(false)} />
    ) : (
      <LoginPage onSwitchToRegister={() => setIsRegisterView(true)} />
    );
  }

  return <MainDashboard />;
}

export default function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  );
}
