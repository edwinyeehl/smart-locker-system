'use client';

export default function MobileFeed({ notifications, onClearNotifications }) {
  return (
    <div 
      className="glass-panel" 
      style={{ 
        padding: '24px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px', 
        background: '#ffffff', 
        minHeight: '600px', 
        borderRadius: '32px', 
        border: '6px solid #e5e7eb', 
        boxShadow: '0 10px 30px rgba(0,0,0,0.08)', 
        position: 'relative' 
      }}
    >
      {/* Phone Notch */}
      <div style={{ width: '120px', height: '18px', background: '#1f2937', borderRadius: '0 0 12px 12px', position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', zIndex: 10 }}></div>
      
      {/* Mobile Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: '700' }}>
        <span>📲 SMS & Email Notifications</span>
        <button 
          onClick={onClearNotifications}
          style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', fontWeight: '700' }}
        >
          Clear All
        </button>
      </div>
      
      <hr style={{ borderColor: '#f3f4f6', margin: '0' }} />

      {/* Notification logs list */}
      <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
        <span>💬</span> Received Alerts
      </h3>
      
      <div className="notification-feed" style={{ flex: 1 }}>
        {notifications.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', gap: '10px', padding: '40px 0' }}>
            <span style={{ fontSize: '2.5rem' }}>📭</span>
            <p style={{ fontSize: '0.85rem' }}>No incoming SMS alerts enqueued.<br/>Perform a parcel deposit to trigger alerts.</p>
          </div>
        ) : (
          notifications.map(notif => (
            <div key={notif.id} className="notification-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: '800', marginBottom: '6px' }}>
                <span>📱 {notif.recipient_phone}</span>
                <span style={{ color: 'var(--text-muted)', fontWeight: '500' }}>{new Date(notif.timestamp).toLocaleTimeString()}</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: '1.4' }}>{notif.message}</p>
              
              {/* Pickup PIN Card */}
              <div style={{ marginTop: '10px', background: '#fff5f3', padding: '8px 12px', borderRadius: '8px', border: '1px dashed var(--color-primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: '600' }}>Pickup Code:</span>
                <strong style={{ fontSize: '1.1rem', color: 'var(--color-primary)', letterSpacing: '2px', fontFamily: 'var(--font-display)' }}>{notif.raw_code}</strong>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
