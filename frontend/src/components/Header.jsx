'use client';

export default function Header({ stations, selectedStationId, setSelectedStationId, onOpenInitModal }) {
  return (
    <header 
      className="glass-panel" 
      style={{ 
        padding: '20px 30px', 
        display: 'flex', 
        justify: 'space-between', 
        alignItems: 'center', 
        flexWrap: 'wrap', 
        gap: '15px', 
        borderTop: '4px solid var(--color-primary)' 
      }}
    >
      <div>
        <h1 style={{ fontSize: '1.8rem', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>🧡</span> SHOPEE EXPRESS SMART LOCKER
        </h1>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Smart Package Locker Hub & Terminal Simulator
        </p>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="form-group" style={{ margin: 0 }}>
          <select 
            className="form-select" 
            value={selectedStationId} 
            onChange={(e) => setSelectedStationId(e.target.value)}
            style={{ padding: '10px 14px', fontSize: '0.9rem', width: '250px', background: '#ffffff', fontWeight: '600' }}
          >
            <option value="">-- Select Locker Station --</option>
            {stations.map(st => (
              <option key={st.id} value={st.id}>{st.name}</option>
            ))}
          </select>
        </div>
        
        <button 
          className="btn-primary" 
          onClick={onOpenInitModal}
          style={{ padding: '10px 16px', fontSize: '0.85rem' }}
        >
          ➕ New Station
        </button>
      </div>
    </header>
  );
}
