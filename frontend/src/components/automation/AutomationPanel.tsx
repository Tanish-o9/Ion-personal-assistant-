import { useState, useEffect } from 'react';
import { HiOutlineClock, HiOutlinePlay, HiOutlinePause, HiOutlineTrash, HiOutlinePlus } from 'react-icons/hi';
import { getAutomations, createAutomation, runAutomation, pauseAutomation, resumeAutomation, deleteAutomation } from '../../services/api';

export default function AutomationPanel() {
  const [automations, setAutomations] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [workflowText, setWorkflowText] = useState('');
  const [scheduleCron, setScheduleCron] = useState('0 9 * * 1');
  const [isCreating, setIsCreating] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const loadAutomations = async () => {
    try {
      const data = await getAutomations();
      if (Array.isArray(data)) setAutomations(data);
    } catch (err: any) {
      console.error('Failed to load automations:', err);
    }
  };

  useEffect(() => {
    loadAutomations();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !workflowText.trim()) return;
    setErrorMsg('');
    try {
      await createAutomation({
        name,
        workflow_text: workflowText,
        schedule_cron: scheduleCron,
        timezone: 'UTC',
      });
      setName('');
      setWorkflowText('');
      setIsCreating(false);
      loadAutomations();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to create automation');
    }
  };

  const handleRun = async (id: string) => {
    try {
      await runAutomation(id);
      loadAutomations();
    } catch (err: any) {
      console.error('Failed to run automation:', err);
    }
  };

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      if (enabled) {
        await pauseAutomation(id);
      } else {
        await resumeAutomation(id);
      }
      loadAutomations();
    } catch (err: any) {
      console.error('Failed to toggle automation:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteAutomation(id);
      loadAutomations();
    } catch (err: any) {
      console.error('Failed to delete automation:', err);
    }
  };

  return (
    <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic font-sans">
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <HiOutlineClock className="text-brand-400" size={22} />
          <h3 className="text-lg font-semibold text-white">Workflow Automations</h3>
        </div>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="inline-flex items-center gap-1.5 rounded-2xl bg-brand-500/15 px-3.5 py-2 text-xs font-medium text-brand-200 transition hover:bg-brand-500/25"
        >
          <HiOutlinePlus size={16} /> {isCreating ? 'Cancel' : 'New Automation'}
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="mb-4 rounded-2xl border border-white/10 bg-slate-950/80 p-4 space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Automation Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Weekly Research Summary"
              className="w-full rounded-xl border border-white/10 bg-slate-900 p-2.5 text-xs text-slate-100 outline-none focus:border-brand-400"
              required
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Workflow Prompt / Task</label>
            <textarea
              value={workflowText}
              onChange={(e) => setWorkflowText(e.target.value)}
              placeholder="e.g. Research latest AI developments and summarize key findings"
              rows={2}
              className="w-full rounded-xl border border-white/10 bg-slate-900 p-2.5 text-xs text-slate-100 outline-none focus:border-brand-400 resize-none"
              required
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Schedule (Cron syntax)</label>
            <input
              type="text"
              value={scheduleCron}
              onChange={(e) => setScheduleCron(e.target.value)}
              placeholder="0 9 * * 1"
              className="w-full rounded-xl border border-white/10 bg-slate-900 p-2.5 text-xs font-mono text-slate-100 outline-none focus:border-brand-400"
            />
          </div>

          {errorMsg && <p className="text-xs text-rose-400">{errorMsg}</p>}

          <button
            type="submit"
            className="w-full rounded-xl bg-brand-500 p-2.5 text-xs font-semibold text-slate-950 transition hover:bg-brand-400"
          >
            Create Automation
          </button>
        </form>
      )}

      <div className="space-y-3">
        {automations.length > 0 ? (
          automations.map((auto) => (
            <div key={auto.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/5 bg-slate-950/60 p-3.5 text-xs">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white">{auto.name}</span>
                  <span className={`rounded-full px-2 py-0.5 font-mono text-[10px] ${auto.enabled ? 'bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-400/20' : 'bg-slate-700/30 text-slate-400'}`}>
                    {auto.enabled ? 'Active' : 'Paused'}
                  </span>
                </div>
                <p className="text-slate-400 font-mono text-[11px] truncate max-w-md">{auto.workflow_text}</p>
                <p className="text-slate-500 font-mono text-[10px]">Schedule: {auto.schedule_cron} ({auto.timezone})</p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleRun(auto.id)}
                  title="Run now"
                  className="rounded-xl bg-brand-500/15 p-2 text-brand-300 transition hover:bg-brand-500/25"
                >
                  <HiOutlinePlay size={16} />
                </button>
                <button
                  onClick={() => handleToggle(auto.id, auto.enabled)}
                  title={auto.enabled ? 'Pause' : 'Resume'}
                  className="rounded-xl bg-slate-800 p-2 text-slate-300 transition hover:bg-slate-700"
                >
                  {auto.enabled ? <HiOutlinePause size={16} /> : <HiOutlinePlay size={16} />}
                </button>
                <button
                  onClick={() => handleDelete(auto.id)}
                  title="Delete"
                  className="rounded-xl bg-rose-500/10 p-2 text-rose-400 transition hover:bg-rose-500/20"
                >
                  <HiOutlineTrash size={16} />
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-500 italic">No scheduled automations configured.</p>
        )}
      </div>
    </div>
  );
}
