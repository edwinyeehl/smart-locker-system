'use client';

import { useState } from 'react';

export default function EngineerForm({ engineer, onLoginEngineer, onLogoutEngineer }) {
  const [engUsername, setEngUsername] = useState('admin_engineer');
  const [engPassword, setEngPassword] = useState('admin123');

  const handleLogin = (e) => {
    e.preventDefault();
    onLoginEngineer({ engUsername, engPassword });
  };

  if (!engineer) {
    return (
      <form onSubmit={handleLogin}>
        <h3 style={{ marginBottom: '16px', color: 'var(--color-primary)' }}>Engineer Maintenance Login</h3>
        <div className="form-group">
          <label className="form-label">Engineer Username</label>
          <input className="form-input" type="text" value={engUsername} onChange={e => setEngUsername(e.target.value)} required />
        </div>
        <div className="form-group">
          <label className="form-label">Verification Password</label>
          <input className="form-input" type="password" value={engPassword} onChange={e => setEngPassword(e.target.value)} required />
        </div>
        <button className="btn-primary" type="submit" style={{ width: '100%', marginTop: '10px' }}>
          🔑 Authenticate Engineer
        </button>
      </form>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3>Engineer Controls Active</h3>
        <button className="btn-secondary" onClick={onLogoutEngineer} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>Logout</button>
      </div>
      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
        Authenticated: <strong style={{ color: 'var(--color-primary)' }}>{engineer.username}</strong> ({engineer.engineer_code}).
      </p>
      <div className="glass-panel" style={{ padding: '16px', background: '#fef3c7', borderColor: '#f59e0b' }}>
        <p style={{ fontSize: '0.85rem', color: '#b45309', fontWeight: '700' }}>
          💡 Maintenance Mode Toggle:
        </p>
        <p style={{ fontSize: '0.8rem', color: '#92400e', marginTop: '4px' }}>
          Click on any slot card in the shelf view above to toggle its maintenance state. Maintenance slots cannot be allocated.
        </p>
      </div>
    </div>
  );
}
