'use client';

import { useState } from 'react';

export default function RetrievalForm({ onSubmitRetrieval }) {
  const [retrievalPhone, setRetrievalPhone] = useState('+60123456789');
  const [retrievalCode, setRetrievalCode] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitRetrieval({
      retrievalPhone,
      retrievalCode
    });
    setRetrievalCode('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '16px', color: 'var(--color-primary)' }}>Recipient Self-Collection Kiosk</h3>
      
      <div className="form-group">
        <label className="form-label">Recipient Phone Number (MY +60)</label>
        <input className="form-input" type="text" placeholder="+60123456789" value={retrievalPhone} onChange={e => setRetrievalPhone(e.target.value)} required />
      </div>

      <div className="form-group">
        <label className="form-label">6-Digit Secure SMS Pickup PIN</label>
        <input className="form-input" type="text" placeholder="e.g. 582910" value={retrievalCode} onChange={e => setRetrievalCode(e.target.value)} required />
      </div>

      <button className="btn-primary" type="submit" style={{ width: '100%', marginTop: '10px' }}>
        🔑 Unlock Locker for Parcel Collection
      </button>
    </form>
  );
}
