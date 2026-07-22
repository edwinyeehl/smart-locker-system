'use client';

import { useState } from 'react';

export default function P2PForm({ onSubmitP2PDeposit }) {
  const [p2pStorerName, setP2pStorerName] = useState('Siti Nurhaliza');
  const [p2pStorerPhone, setP2pStorerPhone] = useState('+60198765432');
  const [p2pRecipientName, setP2pRecipientName] = useState('Chong Wei');
  const [p2pRecipientPhone, setP2pRecipientPhone] = useState('+60123456789');
  const [p2pRecipientEmail, setP2pRecipientEmail] = useState('chongwei@example.com.my');
  const [p2pSize, setP2pSize] = useState('SMALL');
  const [p2pPaymentAmount, setP2pPaymentAmount] = useState('10.00');
  const [p2pAgreed, setP2pAgreed] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitP2PDeposit({
      p2pStorerName,
      p2pStorerPhone,
      p2pRecipientName,
      p2pRecipientPhone,
      p2pRecipientEmail,
      p2pSize,
      p2pPaymentAmount,
      p2pAgreed
    });
    setP2pAgreed(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3 style={{ marginBottom: '16px', color: 'var(--color-primary)' }}>P2P (Peer-to-Peer) Parcel Deposit</h3>
      
      <h4 style={{ fontSize: '0.9rem', color: 'var(--color-primary)', marginBottom: '10px' }}>Storer Details</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">Your Name</label>
          <input className="form-input" type="text" placeholder="Siti Nurhaliza" value={p2pStorerName} onChange={e => setP2pStorerName(e.target.value)} required />
        </div>
        <div className="form-group">
          <label className="form-label">Your Phone</label>
          <input className="form-input" type="text" placeholder="+60198765432" value={p2pStorerPhone} onChange={e => setP2pStorerPhone(e.target.value)} required />
        </div>
      </div>

      <h4 style={{ fontSize: '0.9rem', color: 'var(--color-secondary)', margin: '12px 0 10px 0' }}>Recipient Details</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">Recipient Phone (MY +60)</label>
          <input className="form-input" type="text" placeholder="+60123456789" value={p2pRecipientPhone} onChange={e => setP2pRecipientPhone(e.target.value)} required />
        </div>
        <div className="form-group">
          <label className="form-label">Recipient Name</label>
          <input className="form-input" type="text" placeholder="Chong Wei" value={p2pRecipientName} onChange={e => setP2pRecipientName(e.target.value)} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '8px' }}>
        <div className="form-group">
          <label className="form-label">Parcel Size</label>
          <select className="form-select" value={p2pSize} onChange={e => setP2pSize(e.target.value)}>
            <option value="SMALL">Small</option>
            <option value="MEDIUM">Medium</option>
            <option value="LARGE">Large</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Upfront Payment (RM 10.00 Base Rate)</label>
          <input className="form-input" type="number" step="0.01" value={p2pPaymentAmount} onChange={e => setP2pPaymentAmount(e.target.value)} required />
        </div>
      </div>

      <div className="form-group" style={{ margin: '10px 0 16px 0' }}>
        <label className="form-checkbox-label">
          <input type="checkbox" checked={p2pAgreed} onChange={e => setP2pAgreed(e.target.checked)} style={{ cursor: 'pointer' }} required />
          I agree to the Terms & Conditions (No prohibited or dangerous items)
        </label>
      </div>

      <button className="btn-primary" type="submit" style={{ width: '100%' }}>
        💳 Pay Upfront & Deposit Parcel
      </button>
    </form>
  );
}
