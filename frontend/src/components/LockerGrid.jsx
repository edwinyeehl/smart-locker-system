'use client';

export default function LockerGrid({ slots, selectedStation, activeTab, onToggleSlotMaintenance }) {
  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>📦</span> Live Locker Shelf Status
          </h2>
          {selectedStation && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              📍 {selectedStation.address}
            </p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: '600' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-available)' }}></span> Available
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-reserved)' }}></span> Reserved
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-occupied)' }}></span> Occupied
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-maintenance)' }}></span> Maintenance
          </span>
        </div>
      </div>
      
      {slots.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: '1rem' }}>No locker slots found for this station.</p>
        </div>
      ) : (
        <div className="locker-grid">
          {slots.map(slot => (
            <div 
              key={slot.id} 
              className={`locker-slot-card ${slot.status.toLowerCase()}`}
              onClick={() => {
                if (activeTab === 'engineer') {
                  onToggleSlotMaintenance(slot.id, slot.slot_code);
                }
              }}
            >
              <span style={{ fontSize: '1.3rem', fontWeight: '800', fontFamily: 'var(--font-display)', color: 'var(--text-primary)' }}>{slot.slot_code}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px', fontWeight: '600' }}>Size: {slot.size}</span>
              <span className={`status-badge ${slot.status.toLowerCase()}`}>{slot.status}</span>
              
              {activeTab === 'engineer' && (
                <span style={{ fontSize: '0.65rem', color: 'var(--color-primary)', marginTop: '8px', fontWeight: '700' }}>👉 Click to Toggle</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
