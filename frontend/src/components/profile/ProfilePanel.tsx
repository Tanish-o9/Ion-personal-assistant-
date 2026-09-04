import { useEffect, useState, useCallback } from 'react';
import { HiOutlineUserCircle, HiOutlineCog } from 'react-icons/hi';
import { fetchUserProfile } from '../../services/api';

interface UserProfileData {
  user_id: string;
  username: string;
  total_memories: number;
  preferences: string[];
  projects: string[];
  instructions: string[];
  status: string;
}

interface ProfilePanelProps {
  userId?: string;
}

export default function ProfilePanel({ userId = 'default_user' }: ProfilePanelProps) {
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUserProfile(userId);
      setProfile(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load user profile.');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-6 shadow-futuristic">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500/15 text-brand-300 ring-1 ring-brand-400/20">
          <HiOutlineUserCircle size={26} />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">User Intelligence</p>
          <h3 className="text-xl font-semibold text-white">User Profile</h3>
        </div>
      </div>

      {loading ? (
        <p className="py-8 text-center text-xs text-slate-500">Loading user profile...</p>
      ) : error ? (
        <p className="py-4 text-xs text-rose-400">{error}</p>
      ) : profile ? (
        <div className="space-y-4 text-xs">
          <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-4 grid grid-cols-2 gap-4">
            <div>
              <span className="text-slate-500 font-semibold block mb-1">User ID:</span>
              <span className="text-white font-mono">{profile.user_id}</span>
            </div>
            <div>
              <span className="text-slate-500 font-semibold block mb-1">Total Memories:</span>
              <span className="text-brand-300 font-bold">{profile.total_memories}</span>
            </div>
          </div>

          {profile.preferences.length > 0 && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
              <span className="text-slate-400 font-semibold block mb-2">Preferences:</span>
              <ul className="list-disc list-inside space-y-1 text-slate-200">
                {profile.preferences.map((pref, i) => (
                  <li key={i}>{pref}</li>
                ))}
              </ul>
            </div>
          )}

          {profile.projects.length > 0 && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
              <span className="text-slate-400 font-semibold block mb-2">Active Projects:</span>
              <ul className="list-disc list-inside space-y-1 text-slate-200">
                {profile.projects.map((proj, i) => (
                  <li key={i}>{proj}</li>
                ))}
              </ul>
            </div>
          )}

          {profile.instructions.length > 0 && (
            <div className="rounded-2xl border border-white/10 bg-slate-950/80 p-4">
              <span className="text-slate-400 font-semibold block mb-2">Custom Instructions:</span>
              <ul className="list-disc list-inside space-y-1 text-slate-200">
                {profile.instructions.map((inst, i) => (
                  <li key={i}>{inst}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
