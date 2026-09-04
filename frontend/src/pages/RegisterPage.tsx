import { useState, useContext } from 'react';
import { HiOutlineSparkles, HiOutlineLockClosed, HiOutlineUser } from 'react-icons/hi';
import { AuthContext } from '../contexts/AuthContext';

interface RegisterPageProps {
  onSwitchToLogin: () => void;
}

export default function RegisterPage({ onSwitchToLogin }: RegisterPageProps) {
  const { register } = useContext(AuthContext);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await register(username.trim(), password.trim());
    } catch (err: any) {
      setError(err?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12 text-slate-100 font-sans">
      <div className="w-full max-w-md rounded-[2.5rem] border border-white/10 bg-slate-900/80 p-8 shadow-futuristic backdrop-blur-xl">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500/15 text-brand-300 ring-1 ring-brand-400/20 mb-4">
            <HiOutlineSparkles size={28} />
          </div>
          <h1 className="text-2xl font-bold text-white">Create Account</h1>
          <p className="mt-1 text-xs text-slate-400">Register for multi-user isolated ION access</p>
        </div>

        {error && (
          <div className="mb-6 rounded-2xl border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-400 mb-2 font-medium">Username</label>
            <div className="relative">
              <HiOutlineUser size={18} className="absolute left-4 top-3.5 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 pl-11 pr-4 py-3 text-sm text-white outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10"
                placeholder="Choose a username"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-400 mb-2 font-medium">Password</label>
            <div className="relative">
              <HiOutlineLockClosed size={18} className="absolute left-4 top-3.5 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 pl-11 pr-4 py-3 text-sm text-white outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10"
                placeholder="Choose a password"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-400 mb-2 font-medium">Confirm Password</label>
            <div className="relative">
              <HiOutlineLockClosed size={18} className="absolute left-4 top-3.5 text-slate-500" />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/80 pl-11 pr-4 py-3 text-sm text-white outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10"
                placeholder="Confirm your password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-brand-500 py-3.5 text-sm font-semibold text-slate-950 shadow-lg shadow-brand-500/20 transition hover:bg-brand-400 disabled:opacity-60"
          >
            {loading ? 'Registering...' : 'Register Account'}
          </button>
        </form>

        <div className="mt-8 text-center text-xs text-slate-400">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="text-brand-300 hover:underline font-semibold">
            Sign in here
          </button>
        </div>
      </div>
    </div>
  );
}
