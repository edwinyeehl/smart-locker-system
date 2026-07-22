'use client';

export default function SystemLogs({ systemLogs }) {
  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.05rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)' }}>
        <span>📄</span> System Activity Event Monitor
      </h3>
      <div style={{ background: '#1e293b', color: '#f8fafc', padding: '16px', borderRadius: '10px', height: '150px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.8rem' }}>
        {systemLogs.length === 0 ? (
          <div style={{ color: '#94a3b8' }}>Waiting for system events...</div>
        ) : (
          systemLogs.map((log, idx) => (
            <div key={idx} style={{ marginBottom: '6px', color: log.type === 'error' ? '#f87171' : log.type === 'success' ? '#34d399' : '#94a3b8' }}>
              [{log.timestamp}] {log.message}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
