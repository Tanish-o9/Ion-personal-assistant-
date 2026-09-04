import React, { useState } from 'react';

interface PolicyData {
  organizationId: string;
  workspaceId: string;
  allowedModels: string[];
  maxBudgetUsd: number;
  dataResidency: string;
}

export const EnterpriseDashboardPage: React.FC = () => {
  const [policy, setPolicy] = useState<PolicyData>({
    organizationId: 'org-enterprise-1',
    workspaceId: 'ws-prod',
    allowedModels: ['gpt-4o', 'claude-3-5-sonnet', 'jarvis-v5'],
    maxBudgetUsd: 5000,
    dataResidency: 'us-east-1',
  });

  const [message, setMessage] = useState<string>('');

  const handleSavePolicy = () => {
    setMessage('Enterprise Policy saved successfully.');
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>JARVIS 5.0 Enterprise Admin Dashboard</h1>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        Manage Organizations, Workspaces, Data Residency, Capability Governance, and Multi-Tier Budgets.
      </p>

      {message && (
        <div style={{ padding: '12px', backgroundColor: '#059669', color: '#ffffff', borderRadius: '6px', marginBottom: '16px' }}>
          {message}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '12px' }}>Organization & Workspace Policy</h2>
          
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Organization ID</label>
            <input
              type="text"
              value={policy.organizationId}
              onChange={(e) => setPolicy({ ...policy, organizationId: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', backgroundColor: '#334155', color: '#fff', border: '1px solid #475569' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Workspace ID</label>
            <input
              type="text"
              value={policy.workspaceId}
              onChange={(e) => setPolicy({ ...policy, workspaceId: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', backgroundColor: '#334155', color: '#fff', border: '1px solid #475569' }}
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Max Monthly Budget (USD)</label>
            <input
              type="number"
              value={policy.maxBudgetUsd}
              onChange={(e) => setPolicy({ ...policy, maxBudgetUsd: Number(e.target.value) })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', backgroundColor: '#334155', color: '#fff', border: '1px solid #475569' }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Data Residency Region</label>
            <select
              value={policy.dataResidency}
              onChange={(e) => setPolicy({ ...policy, dataResidency: e.target.value })}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', backgroundColor: '#334155', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="us-east-1">US East (N. Virginia)</option>
              <option value="us-west-2">US West (Oregon)</option>
              <option value="eu-central-1">EU Central (Frankfurt)</option>
              <option value="ap-southeast-1">AP Southeast (Singapore)</option>
            </select>
          </div>

          <button
            onClick={handleSavePolicy}
            style={{ backgroundColor: '#2563eb', color: '#fff', padding: '10px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}
          >
            Save Policy Settings
          </button>
        </div>

        <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '12px' }}>Global Health & Multi-Region Nodes</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ padding: '8px 0', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between' }}>
              <span>us-east-1 (US East)</span>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>HEALTHY (100%)</span>
            </li>
            <li style={{ padding: '8px 0', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between' }}>
              <span>us-west-2 (US West)</span>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>HEALTHY (100%)</span>
            </li>
            <li style={{ padding: '8px 0', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between' }}>
              <span>eu-central-1 (EU Central)</span>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>HEALTHY (100%)</span>
            </li>
            <li style={{ padding: '8px 0', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between' }}>
              <span>ap-southeast-1 (AP Southeast)</span>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>HEALTHY (100%)</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
