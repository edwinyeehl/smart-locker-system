'use client';

export default function UnlockAlert({ 
  unlockedSlot, 
  unlockedSlotAction, 
  retrievedAllocation, 
  onConfirmDeposit, 
  onCancelDeposit, 
  onCompleteRetrieval 
}) {
  if (!unlockedSlot) return null;

  return (
    <div 
      className="glass-panel" 
      style={{ 
        padding: '20px 24px', 
        borderColor: 'var(--color-primary)', 
        background: '#fff5f3', 
        display: 'flex', 
        justify: 'space-between', 
        alignItems: 'center', 
        flexWrap: 'wrap', 
        gap: '15px' 
      }}
    >
      <div>
        <h3 style={{ color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          🔓 LOCKER DOOR UNLOCKED
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Slot <strong style={{ color: 'var(--text-primary)' }}>{unlockedSlot.slot_code}</strong> ({unlockedSlot.size}) physical door open.
        </p>
        {unlockedSlotAction === 'retrieve' && retrievedAllocation && (
          <p style={{ fontSize: '0.85rem', color: 'var(--color-primary)', marginTop: '4px', fontWeight: '700' }}>
            Storage Charge Due: <strong>RM {parseFloat(retrievedAllocation.total_charge_applied || 0).toFixed(2)}</strong>.
          </p>
        )}
        {unlockedSlotAction === 'deposit' && (
          <p style={{ fontSize: '0.85rem', color: 'var(--color-available)', marginTop: '4px', fontWeight: '700' }}>
            Place package inside, then close door to send SMS PIN. Or cancel to abort deposit.
          </p>
        )}
      </div>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        {unlockedSlotAction === 'deposit' ? (
          <>
            <button 
              className="btn-secondary" 
              onClick={onCancelDeposit}
              style={{ padding: '10px 16px', fontSize: '0.85rem', color: '#dc2626', borderColor: '#fca5a5' }}
            >
              ❌ Cancel Deposit
            </button>
            <button 
              className="btn-primary" 
              onClick={onConfirmDeposit}
              style={{ padding: '10px 18px', fontSize: '0.85rem' }}
            >
              🚪 Close Door & Dispatch SMS
            </button>
          </>
        ) : (
          <button 
            className="btn-primary" 
            onClick={onCompleteRetrieval}
            style={{ padding: '10px 18px', fontSize: '0.85rem' }}
          >
            🚪 Close Locker Door (Complete Retrieval)
          </button>
        )}
      </div>
    </div>
  );
}
