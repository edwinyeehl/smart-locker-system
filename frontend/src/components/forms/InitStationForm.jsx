'use client';

import { useState } from 'react';

export default function InitStationForm({ onSubmitInitStation, onCancel }) {
  const [initName, setInitName] = useState('Sunway Pyramid Station');
  const [initAddress, setInitAddress] = useState('Sunway Pyramid, 3, Jalan PJS 11/15, Bandar Sunway, 47500 Subang Jaya');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitInitStation({ initName, initAddress });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '16px', color: 'var(--color-primary)' }}>Initialize New Locker Station</h3>
      
      <div className="form-group">
        <label className="form-label">Station Name</label>
        <input className="form-input" type="text" placeholder="e.g. Pavilion Bukit Jalil Station" value={initName} onChange={e => setInitName(e.target.value)} required />
      </div>

      <div className="form-group">
        <label className="form-label">Physical Location Address</label>
        <input className="form-input" type="text" placeholder="e.g. 2, Jalan Bukit Jalil 2, 57000 Kuala Lumpur" value={initAddress} onChange={e => setInitAddress(e.target.value)} required />
      </div>

      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        <button className="btn-primary" type="submit" style={{ flex: 1 }}>
          🚀 Initialize & Seed Slots
        </button>
        <button className="btn-secondary" type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
