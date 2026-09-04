import { useState, useEffect } from 'react';
import { HiOutlineCog, HiOutlineCheckCircle, HiOutlineExclamationCircle, HiOutlineBan } from 'react-icons/hi';
import { fetchUserJobs, cancelJob } from '../../services/api';

export interface BackgroundJobItem {
  id: string;
  user_id: string;
  session_id: string;
  job_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  result?: string;
  error?: string;
  created_at: string;
}

export default function JobsPanel() {
  const [jobs, setJobs] = useState<BackgroundJobItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadJobs = async () => {
    try {
      const data = await fetchUserJobs();
      setJobs(data);
    } catch (err) {
      console.error('Failed to load background jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (jobId: string) => {
    try {
      await cancelJob(jobId);
      loadJobs();
    } catch (err) {
      console.error('Failed to cancel job:', err);
    }
  };

  if (loading) {
    return (
      <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-4 text-xs text-slate-400">
        Loading background tasks...
      </div>
    );
  }

  if (jobs.length === 0) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 shadow-futuristic backdrop-blur-xl mb-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <HiOutlineCog size={20} className="text-brand-400 animate-spin-slow" />
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Background Tasks</h3>
        </div>
        <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-xs text-brand-300 ring-1 ring-brand-400/20">
          {jobs.filter((j) => j.status === 'running' || j.status === 'pending').length} Active
        </span>
      </div>

      <div className="space-y-3">
        {jobs.slice(0, 5).map((job) => (
          <div key={job.id} className="rounded-2xl border border-white/5 bg-slate-950/70 p-3.5 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-medium text-slate-200">
                <span className="capitalize">{job.job_type.replace('_', ' ')} Task</span>
              </div>
              <div className="flex items-center gap-2">
                {job.status === 'completed' && <HiOutlineCheckCircle size={16} className="text-emerald-400" />}
                {job.status === 'failed' && <HiOutlineExclamationCircle size={16} className="text-rose-400" />}
                {job.status === 'cancelled' && <HiOutlineBan size={16} className="text-amber-400" />}
                <span
                  className={`capitalize font-semibold text-[11px] ${
                    job.status === 'completed'
                      ? 'text-emerald-400'
                      : job.status === 'failed'
                      ? 'text-rose-400'
                      : job.status === 'cancelled'
                      ? 'text-amber-400'
                      : 'text-brand-400'
                  }`}
                >
                  {job.status}
                </span>
                {(job.status === 'pending' || job.status === 'running') && (
                  <button
                    onClick={() => handleCancel(job.id)}
                    className="text-[10px] text-slate-400 hover:text-rose-400 transition"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>

            <div className="relative h-2 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full transition-all duration-300 ${
                  job.status === 'failed'
                    ? 'bg-rose-500'
                    : job.status === 'cancelled'
                    ? 'bg-amber-500'
                    : 'bg-brand-500'
                }`}
                style={{ width: `${job.progress}%` }}
              />
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="truncate">{job.result || job.error || 'Processing in background...'}</span>
              <span>{job.progress}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
