'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import LockerGrid from '@/components/LockerGrid';
import UnlockAlert from '@/components/UnlockAlert';
import SystemLogs from '@/components/SystemLogs';
import MobileFeed from '@/components/MobileFeed';

import CourierForm from '@/components/forms/CourierForm';
import P2PForm from '@/components/forms/P2PForm';
import RetrievalForm from '@/components/forms/RetrievalForm';
import EngineerForm from '@/components/forms/EngineerForm';
import InitStationForm from '@/components/forms/InitStationForm';

const API_BASE = 'http://127.0.0.1:8000/api';

export default function Home() {
  // App Core State
  const [stations, setStations] = useState([]);
  const [selectedStationId, setSelectedStationId] = useState('');
  const [slots, setSlots] = useState([]);
  const [activeTab, setActiveTab] = useState('courier');
  const [notifications, setNotifications] = useState([]);
  
  // Door Simulation & Pending Deposit State
  const [unlockedSlot, setUnlockedSlot] = useState(null);
  const [unlockedSlotAction, setUnlockedSlotAction] = useState(null); // 'deposit' | 'retrieve'
  const [pendingAllocation, setPendingAllocation] = useState(null); // { allocation_id, raw_code }
  const [retrievedAllocation, setRetrievedAllocation] = useState(null);
  const [systemLogs, setSystemLogs] = useState([]);

  // Engineer Auth State
  const [engineer, setEngineer] = useState(null);

  // Add Log Helper
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setSystemLogs(prev => [{ timestamp, message, type }, ...prev].slice(0, 50));
  };

  // Fetch Stations
  const fetchStations = async () => {
    try {
      const res = await fetch(`${API_BASE}/stations`);
      if (res.ok) {
        const data = await res.json();
        setStations(data);
        if (data.length > 0 && !selectedStationId) {
          setSelectedStationId(data[0].id);
        }
      }
    } catch (err) {
      console.error("Error fetching stations:", err);
    }
  };

  // Fetch Slots
  const fetchSlots = async () => {
    if (!selectedStationId) return;
    try {
      const res = await fetch(`${API_BASE}/stations/${selectedStationId}/slots`);
      if (res.ok) {
        const data = await res.json();
        setSlots(data);
      }
    } catch (err) {
      console.error("Error fetching slots:", err);
    }
  };

  // Fetch Notifications
  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/notifications`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.reverse());
      }
    } catch (err) {
      console.error("Error fetching notifications:", err);
    }
  };

  // Clear Notifications
  const handleClearNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/notifications/clear`, { method: 'POST' });
      if (res.ok) {
        addLog("Notification feeds cleared.", "info");
        fetchNotifications();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Handlers
  const handleInitializeStation = async ({ initName, initAddress }) => {
    try {
      const res = await fetch(`${API_BASE}/stations/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: initName,
          address: initAddress,
          seed_slots: true
        })
      });
      if (res.ok) {
        const data = await res.json();
        addLog(`Locker station '${data.name}' initialized with 6 slots.`, 'success');
        fetchStations();
        setSelectedStationId(data.id);
        setActiveTab('courier');
      } else {
        const errData = await res.json();
        addLog(`Station initialization failed: ${errData.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error initializing station: ${err.message}`, 'error');
    }
  };

  const handleCourierDeposit = async ({ courierName, courierCode, courierPackageId, courierSize, courierPhone }) => {
    if (!selectedStationId) {
      addLog("Please select a locker station.", "error");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/allocations/deposit-courier`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          station_id: selectedStationId,
          package_identifier: courierPackageId,
          courier_name: courierName,
          courier_code: courierCode,
          recipient_phone: courierPhone,
          package_size: courierSize
        })
      });
      const data = await res.json();
      if (res.ok) {
        addLog(`Courier deposited package ${courierPackageId}. Slot ${data.unlocked_slot.slot_code} unlocked! Waiting for door close to send SMS...`, 'success');
        setUnlockedSlot(data.unlocked_slot);
        setUnlockedSlotAction('deposit');
        setPendingAllocation({ allocation_id: data.allocation.id, raw_code: data.raw_pickup_code });
        fetchSlots();
      } else {
        addLog(`Deposit failed: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error during deposit: ${err.message}`, 'error');
    }
  };

  const handleP2PDeposit = async ({ p2pStorerName, p2pStorerPhone, p2pRecipientName, p2pRecipientPhone, p2pRecipientEmail, p2pSize, p2pPaymentAmount, p2pAgreed }) => {
    if (!selectedStationId) {
      addLog("Please select a locker station.", "error");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/allocations/deposit-p2p`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          station_id: selectedStationId,
          package_size: p2pSize,
          storer_name: p2pStorerName,
          storer_phone: p2pStorerPhone,
          recipient_phone: p2pRecipientPhone,
          recipient_name: p2pRecipientName || null,
          recipient_email: p2pRecipientEmail || null,
          agreed_to_tc: p2pAgreed,
          payment_amount: parseFloat(p2pPaymentAmount)
        })
      });
      const data = await res.json();
      if (res.ok) {
        addLog(`P2P package deposited. Slot ${data.unlocked_slot.slot_code} unlocked. Paid Upfront: RM ${p2pPaymentAmount}. Waiting for door close to send SMS...`, 'success');
        setUnlockedSlot(data.unlocked_slot);
        setUnlockedSlotAction('deposit');
        setPendingAllocation({ allocation_id: data.allocation.id, raw_code: data.raw_pickup_code });
        fetchSlots();
      } else {
        addLog(`P2P deposit failed: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error during P2P deposit: ${err.message}`, 'error');
    }
  };

  // Confirm deposit door closure & dispatch SMS
  const handleConfirmDeposit = async () => {
    if (!pendingAllocation) return;
    try {
      const res = await fetch(`${API_BASE}/allocations/deposit-confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          allocation_id: pendingAllocation.allocation_id,
          raw_code: pendingAllocation.raw_code
        })
      });
      if (res.ok) {
        addLog(`Locker door closed. Package safely stored & SMS notification dispatched to recipient!`, 'success');
        setUnlockedSlot(null);
        setUnlockedSlotAction(null);
        setPendingAllocation(null);
        fetchSlots();
        fetchNotifications();
      } else {
        const data = await res.json();
        addLog(`Failed to confirm deposit door closure: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error confirming deposit: ${err.message}`, 'error');
    }
  };

  // Cancel deposit while door is open
  const handleCancelDeposit = async () => {
    if (!pendingAllocation) return;
    try {
      const res = await fetch(`${API_BASE}/allocations/deposit-cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ allocation_id: pendingAllocation.allocation_id })
      });
      if (res.ok) {
        addLog(`Deposit cancelled by user. Slot ${unlockedSlot?.slot_code || ''} reverted to AVAILABLE. No SMS sent.`, 'info');
        setUnlockedSlot(null);
        setUnlockedSlotAction(null);
        setPendingAllocation(null);
        fetchSlots();
      } else {
        const data = await res.json();
        addLog(`Failed to cancel deposit: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error cancelling deposit: ${err.message}`, 'error');
    }
  };

  const handleRetrieveRequest = async ({ retrievalPhone, retrievalCode }) => {
    if (!selectedStationId) {
      addLog("Please select a locker station.", "error");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/allocations/retrieve-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          station_id: selectedStationId,
          recipient_phone: retrievalPhone,
          pickup_code: retrievalCode
        })
      });
      const data = await res.json();
      if (res.ok) {
        addLog(`Pickup code validated. Slot ${data.unlocked_slot.slot_code} unlocked! Storage charge: RM ${data.total_charge_applied}`, 'success');
        setUnlockedSlot(data.unlocked_slot);
        setUnlockedSlotAction('retrieve');
        setRetrievedAllocation(data.allocation);
        fetchSlots();
      } else {
        addLog(`Retrieval request failed: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error requesting retrieval: ${err.message}`, 'error');
    }
  };

  const handleCompleteRetrieval = async () => {
    if (!unlockedSlot) return;
    try {
      const res = await fetch(`${API_BASE}/allocations/retrieve-complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot_id: unlockedSlot.id })
      });
      if (res.ok) {
        addLog(`Physical door closed for slot ${unlockedSlot.slot_code}. Status marked as AVAILABLE.`, 'success');
        setUnlockedSlot(null);
        setUnlockedSlotAction(null);
        setRetrievedAllocation(null);
        fetchSlots();
      } else {
        const data = await res.json();
        addLog(`Failed to close slot door: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error closing door: ${err.message}`, 'error');
    }
  };

  const handleEngineerLogin = async ({ engUsername, engPassword }) => {
    try {
      const res = await fetch(`${API_BASE}/engineers/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: engUsername, password: engPassword })
      });
      const data = await res.json();
      if (res.ok) {
        setEngineer(data);
        addLog(`Engineer '${data.username}' successfully authenticated.`, 'success');
      } else {
        addLog(`Engineer authentication failed: ${data.detail || 'Invalid username or password'}`, 'error');
      }
    } catch (err) {
      addLog(`Network error authenticating engineer: ${err.message}`, 'error');
    }
  };

  const handleToggleSlotMaintenance = async (slotId, slotCode) => {
    if (!engineer) {
      addLog("Please log in as an engineer first.", "error");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/slots/${slotId}/toggle-maintenance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engineer_id: engineer.id })
      });
      const data = await res.json();
      if (res.ok) {
        addLog(`Slot ${slotCode} status toggled to: ${data.status}`, 'success');
        fetchSlots();
      } else {
        addLog(`Toggle maintenance failed: ${data.detail}`, 'error');
      }
    } catch (err) {
      addLog(`Network error toggling maintenance: ${err.message}`, 'error');
    }
  };

  // Polling loops
  useEffect(() => {
    fetchStations();
    fetchNotifications();
  }, []);

  useEffect(() => {
    fetchSlots();
    const interval = setInterval(fetchSlots, 3000);
    return () => clearInterval(interval);
  }, [selectedStationId]);

  useEffect(() => {
    const interval = setInterval(fetchNotifications, 2000);
    return () => clearInterval(interval);
  }, []);

  const selectedStation = stations.find(s => s.id === selectedStationId);

  return (
    <main style={{ padding: '24px 20px', minHeight: '100vh', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Header Banner */}
      <Header 
        stations={stations} 
        selectedStationId={selectedStationId} 
        setSelectedStationId={setSelectedStationId} 
        onOpenInitModal={() => setActiveTab('init-station')} 
      />

      {/* Main Grid Layout */}
      <div className="simulator-layout">
        
        {/* Left Side: Shelf Display & Simulator Tabs */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Locker Visual Shelf */}
          <LockerGrid 
            slots={slots} 
            selectedStation={selectedStation} 
            activeTab={activeTab} 
            onToggleSlotMaintenance={handleToggleSlotMaintenance} 
          />

          {/* Door Unlocking simulation Alert */}
          <UnlockAlert 
            unlockedSlot={unlockedSlot} 
            unlockedSlotAction={unlockedSlotAction} 
            retrievedAllocation={retrievedAllocation} 
            onConfirmDeposit={handleConfirmDeposit} 
            onCancelDeposit={handleCancelDeposit} 
            onCompleteRetrieval={handleCompleteRetrieval} 
          />

          {/* Actor Control Dashboard */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div className="tab-container" style={{ marginBottom: '20px' }}>
              <button className={`tab-btn ${activeTab === 'courier' ? 'active' : ''}`} onClick={() => setActiveTab('courier')}>🚚 Courier Drop-off</button>
              <button className={`tab-btn ${activeTab === 'p2p' ? 'active' : ''}`} onClick={() => setActiveTab('p2p')}>🤝 P2P Deposit</button>
              <button className={`tab-btn ${activeTab === 'recipient' ? 'active' : ''}`} onClick={() => setActiveTab('recipient')}>🔑 Recipient Collection</button>
              <button className={`tab-btn ${activeTab === 'engineer' ? 'active' : ''}`} onClick={() => setActiveTab('engineer')}>🔧 Engineer Operations</button>
            </div>

            {/* Tab Contents */}
            {activeTab === 'courier' && <CourierForm onSubmitCourierDeposit={handleCourierDeposit} />}
            {activeTab === 'p2p' && <P2PForm onSubmitP2PDeposit={handleP2PDeposit} />}
            {activeTab === 'recipient' && <RetrievalForm onSubmitRetrieval={handleRetrieveRequest} />}
            {activeTab === 'engineer' && (
              <EngineerForm 
                engineer={engineer} 
                onLoginEngineer={handleEngineerLogin} 
                onLogoutEngineer={() => setEngineer(null)} 
              />
            )}
            {activeTab === 'init-station' && (
              <InitStationForm 
                onSubmitInitStation={handleInitializeStation} 
                onCancel={() => setActiveTab('courier')} 
              />
            )}
          </div>

          {/* System event Logger panel */}
          <SystemLogs systemLogs={systemLogs} />

        </section>

        {/* Right Side: Virtual Mobile Phone Alert Feed */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <MobileFeed 
            notifications={notifications} 
            onClearNotifications={handleClearNotifications} 
          />
        </aside>

      </div>
    </main>
  );
}
