import React, { useState } from 'react';

export default function DevicesPage() {
  const [activeTab, setActiveTab] = useState<'devices' | 'environments' | 'scenes' | 'edge' | 'audit'>('devices');

  return (
    <div className="p-6 bg-slate-900 text-slate-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4 text-cyan-400">JARVIS IoT, Smart Environments & Edge Control Center</h1>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-700 mb-6">
        <button
          className={`px-4 py-2 font-medium text-sm border-b-2 ${activeTab === 'devices' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          onClick={() => setActiveTab('devices')}
        >
          Devices
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm border-b-2 ${activeTab === 'environments' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          onClick={() => setActiveTab('environments')}
        >
          Environments
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm border-b-2 ${activeTab === 'scenes' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          onClick={() => setActiveTab('scenes')}
        >
          Smart Scenes
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm border-b-2 ${activeTab === 'edge' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          onClick={() => setActiveTab('edge')}
        >
          Edge Runtime & Privacy
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm border-b-2 ${activeTab === 'audit' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          onClick={() => setActiveTab('audit')}
        >
          Security Audit Feed
        </button>
      </div>

      {/* Panels */}
      {activeTab === 'devices' && (
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Registered IoT Devices</h2>
          <p className="text-slate-400 text-sm mb-4">Permission-controlled IoT devices connected via generic provider adapters.</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-950 rounded border border-slate-700 flex justify-between items-center">
              <div>
                <span className="text-sm font-semibold text-cyan-300">Executive Office Light</span>
                <div className="text-xs text-slate-400 mt-1">Type: LIGHT | Provider: Simulated | Status: ONLINE</div>
                <div className="text-xs text-slate-500">Capabilities: READ_STATUS, SET_STATE, SET_BRIGHTNESS</div>
              </div>
              <button className="px-3 py-1 bg-cyan-700 hover:bg-cyan-600 text-white rounded text-xs">Toggle State</button>
            </div>

            <div className="p-4 bg-slate-950 rounded border border-slate-700 flex justify-between items-center">
              <div>
                <span className="text-sm font-semibold text-purple-300">Conference Room Display</span>
                <div className="text-xs text-slate-400 mt-1">Type: DISPLAY | Provider: Simulated | Status: ONLINE</div>
                <div className="text-xs text-slate-500">Capabilities: READ_STATUS, DISPLAY_MESSAGE</div>
              </div>
              <button className="px-3 py-1 bg-purple-700 hover:bg-purple-600 text-white rounded text-xs">Send Message</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'environments' && (
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Smart Environments</h2>
          <p className="text-slate-400 text-sm mb-4">Coordinated device spaces (Rooms, Offices, Labs) with aggregated state tracking.</p>
          <div className="p-4 bg-slate-950 rounded border border-slate-700">
            <span className="text-sm font-semibold text-cyan-400">Environment: Main Executive Office</span>
            <div className="text-xs text-slate-300 mt-2 space-y-1">
              <div>Devices Connected: 2</div>
              <div>Office Light: ON (Brightness: 80%)</div>
              <div>Thermostat: 22.5 °C</div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'scenes' && (
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Smart Environment Scenes</h2>
          <p className="text-slate-400 text-sm mb-4">Predefined collections of device actions passing risk and approval checks.</p>
          <div className="space-y-3">
            <div className="p-3 bg-slate-950 rounded border border-slate-700 flex justify-between items-center">
              <div>
                <span className="text-xs font-mono text-cyan-400">Scene: Presentation Mode</span>
                <div className="text-xs text-slate-400 mt-1">Actions: Dim Lights to 20%, Display Message on Screen</div>
              </div>
              <button className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs">Execute Scene</button>
            </div>

            <div className="p-3 bg-slate-950 rounded border border-slate-700 flex justify-between items-center">
              <div>
                <span className="text-xs font-mono text-rose-400">Scene: Server Room Power Off</span>
                <div className="text-xs text-slate-400 mt-1">Actions: Cut Critical Server Power (HIGH RISK)</div>
              </div>
              <span className="px-2 py-1 bg-amber-900/60 text-amber-300 rounded text-xs font-mono">Requires Admin Approval</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'edge' && (
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Edge Runtime & Privacy Router</h2>
          <p className="text-slate-400 text-sm mb-4">Capability-aware request routing between Local Edge models and Remote Providers.</p>
          <div className="p-4 bg-slate-950 rounded border border-slate-700 space-y-2 text-xs text-slate-300">
            <div>Local Capabilities: <span className="font-mono text-cyan-300">LOCAL_CLASSIFICATION, LOCAL_CACHE</span></div>
            <div>Privacy Mode: <span className="font-mono text-emerald-400">DEFAULT</span></div>
            <div>Network Status: <span className="font-mono text-emerald-400">ONLINE</span></div>
            <div className="mt-3 p-2 bg-slate-900 rounded border border-slate-800">
              <span className="font-semibold text-slate-200">LOCAL_ONLY Mode Enforcement:</span>
              <p className="text-slate-400 mt-1">When LOCAL_ONLY is enabled, remote provider fallback is strictly blocked to prevent protected data leakage.</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Device Security Audit Feed</h2>
          <p className="text-slate-400 text-sm mb-4">Operational audit log recording authorization, risk levels, approvals, and outcomes.</p>
          <div className="space-y-2 text-xs font-mono">
            <div className="p-2 bg-slate-950 rounded border border-slate-800 flex justify-between text-slate-300">
              <span>dev_1a82 | SET_STATE | Risk: LOW</span>
              <span className="text-emerald-400">COMPLETED</span>
            </div>
            <div className="p-2 bg-slate-950 rounded border border-slate-800 flex justify-between text-slate-300">
              <span>dev_9c41 | SET_TEMPERATURE | Risk: HIGH</span>
              <span className="text-amber-400">WAITING_FOR_APPROVAL (appr_72b0)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
