'use client';

import { useState } from 'react';

export default function CourierForm({ onSubmitCourierDeposit }) {
  const [courierName, setCourierName] = useState('Shopee Xpress');
  const [courierCode, setCourierCode] = useState('SPX-MY99');
  const [courierPackageId, setCourierPackageId] = useState('');
  const [courierSize, setCourierSize] = useState('SMALL');
  const [courierPhone, setCourierPhone] = useState('+60123456789');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitCourierDeposit({
      courierName,
      courierCode,
      courierPackageId,
      courierSize,
      courierPhone
    });
    setCourierPackageId('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '16px', color: 'var(--color-primary)' }}>Courier Drop-off Terminal</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">Courier Service</label>
          <select className="form-select" value={courierName} onChange={e => setCourierName(e.target.value)}>
            <option value="Shopee Xpress">Shopee Xpress (SPX)</option>
            <option value="Pos Laju">Pos Laju</option>
            <option value="J&T Express">J&T Express</option>
            <option value="Ninja Van">Ninja Van</option>
            <option value="GDEX">GDEX</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Courier Verification ID</label>
          <input className="form-input" type="text" value={courierCode} onChange={e => setCourierCode(e.target.value)} required />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Shopee / Courier Tracking ID (Barcode)</label>
        <input className="form-input" type="text" placeholder="e.g. SPXMY09283719" value={courierPackageId} onChange={e => setCourierPackageId(e.target.value)} required />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">Recipient Phone (MY +60)</label>
          <input className="form-input" type="text" placeholder="+60123456789" value={courierPhone} onChange={e => setCourierPhone(e.target.value)} required />
        </div>
        <div className="form-group">
          <label className="form-label">Package Parcel Size</label>
          <select className="form-select" value={courierSize} onChange={e => setCourierSize(e.target.value)}>
            <option value="SMALL">Small (Polymailer / Envelope)</option>
            <option value="MEDIUM">Medium (Shoebox / Box)</option>
            <option value="LARGE">Large (Luggage / Heavy Box)</option>
          </select>
        </div>
      </div>

      <button className="btn-primary" type="submit" style={{ width: '100%', marginTop: '10px' }}>
        🔓 Unlock Slot & Deposit Parcel
      </button>
    </form>
  );
}
