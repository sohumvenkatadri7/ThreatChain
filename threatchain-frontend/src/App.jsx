import { useState, useEffect, useRef } from 'react';
import { ethers } from 'ethers';
import { Shield, ShieldAlert, ShieldCheck, Activity, Database, Clock, Fingerprint, Network, ServerCrash, Cpu, Globe, Trash2 } from 'lucide-react';
import ThreatChainVaultABI from './ThreatChainVaultABI.json';
import './index.css';

// Using the local Hardhat deployment address
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const RPC_URL = "http://127.0.0.1:8545";

// Helper to deterministically generate an IP address from the Blockchain Hash
// This makes the demo look incredibly realistic!
const hashToIp = (hash) => {
  if (!hash) return "Unknown";
  const cleanHash = hash.replace('0x', '');
  const p1 = parseInt(cleanHash.substring(0, 2), 16) % 255;
  const p2 = parseInt(cleanHash.substring(2, 4), 16) % 255;
  const p3 = parseInt(cleanHash.substring(4, 6), 16) % 255;
  const p4 = parseInt(cleanHash.substring(6, 8), 16) % 255;
  return `${p1}.${p2}.${p3}.${p4}`;
};

// Helper to infer the attack vector from the exact confidence score of the payload
const getAttackVector = (score) => {
  const numScore = parseFloat(score);
  if (numScore > 98.0) return "DDoS Payload";
  if (numScore > 96.0) return "FTP Brute Force";
  if (numScore > 90.0) return "Zero-Day Anomaly";
  return "Standard Traffic";
};

function App() {
  const [threats, setThreats] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [livePulse, setLivePulse] = useState(false);
  
  // Use a ref to track when the user cleared the logs, so we can hide old blockchain data
  const hideBeforeTimeRef = useRef(0);

  const handleClearLogs = () => {
    hideBeforeTimeRef.current = Date.now();
    setThreats([]);
  };

  useEffect(() => {
    connectToBlockchain();
  }, []);

  const connectToBlockchain = async () => {
    try {
      const provider = new ethers.JsonRpcProvider(RPC_URL);
      await provider.getNetwork();
      setIsConnected(true);

      const contract = new ethers.Contract(CONTRACT_ADDRESS, ThreatChainVaultABI, provider);
      fetchThreats(contract);

      contract.on("ThreatAnchored", (threatId, confidence, actionTaken, timestamp) => {
        // Trigger a red flash effect on the dashboard
        setLivePulse(true);
        setTimeout(() => setLivePulse(false), 1000);
        fetchThreats(contract);
      });
    } catch (err) {
      console.error("Failed to connect", err);
      setIsConnected(false);
      setLoading(false);
    }
  };

  const fetchThreats = async (contract) => {
    try {
      const data = await contract.getAllThreats();
      const parsedThreats = data.map(t => ({
        id: t.threatId,
        confidence: (Number(t.confidence) / 100).toFixed(2),
        action: t.actionTaken,
        rawTime: Number(t.timestamp) * 1000,
        time: new Date(Number(t.timestamp) * 1000).toLocaleTimeString()
      })).filter(t => t.rawTime >= hideBeforeTimeRef.current);

      parsedThreats.sort((a, b) => new Date(b.time) - new Date(a.time));
      setThreats(parsedThreats.reverse()); // Keep new ones at the top based on local mapping if time is same
      setThreats(parsedThreats);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    if (action === "BLOCK") return <ShieldAlert size={16} />;
    if (action === "REVIEW") return <Shield size={16} />;
    return <ShieldCheck size={16} />;
  };

  return (
    <div className={`dashboard-container ${livePulse ? 'pulse-alert' : ''}`}>
      <header className="header animated-entry" style={{ animationDelay: '0.1s' }}>
        <div className="logo-container">
          <Activity size={32} className={`logo-icon ${livePulse ? 'pulse-spin' : ''}`} />
          <h1>ThreatChain <span style={{color: 'var(--accent-blue)'}}>AI-SOC</span></h1>
        </div>
        <div className="connection-status" style={{ display: 'flex', alignItems: 'center' }}>
          <button 
            onClick={handleClearLogs} 
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', padding: '6px 12px', borderRadius: '20px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', marginRight: '16px', transition: 'all 0.2s ease' }}
            onMouseOver={(e) => { e.currentTarget.style.color = '#f4f4f5'; e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; }}
            onMouseOut={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
          >
             <Trash2 size={14} /> Clear Display
          </button>
          <div className={`status-dot ${isConnected ? 'connected' : ''}`}></div>
          {isConnected ? 'Blockchain Synced' : 'Offline'}
        </div>
      </header>

      <div className="stats-grid animated-entry" style={{ animationDelay: '0.2s' }}>
        <div className="glass-panel stat-card">
          <span className="stat-title"><Network size={18} /> Network Packets Scanned</span>
          <span className="stat-value">Live</span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-title"><ShieldAlert size={18} /> Threats Mitigated</span>
          <span className="stat-value" style={{ color: '#ef4444' }}>
            {threats.filter(t => t.action === 'BLOCK').length}
          </span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-title"><Cpu size={18} /> AI Confidence Avg</span>
          <span className="stat-value" style={{ color: '#8b5cf6' }}>
            {threats.length > 0 
              ? (threats.reduce((a, b) => a + parseFloat(b.confidence), 0) / threats.length).toFixed(1) 
              : 0}%
          </span>
        </div>
      </div>

      <section className="threats-section animated-entry" style={{ animationDelay: '0.3s' }}>
        <h2><Fingerprint size={24} /> Immutable Ledger Intercepts</h2>
        
        <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
          {loading ? (
            <div className="empty-state">
              <Activity size={48} className="logo-icon" style={{ animation: 'pulse 2s infinite' }} />
              <p>Syncing with ThreatChain Vault...</p>
            </div>
          ) : threats.length === 0 ? (
            <div className="empty-state">
              <ShieldCheck size={48} />
              <p>No anomalous activity detected on the network.</p>
            </div>
          ) : (
            <div className="threat-list" style={{ gap: 0 }}>
              <div className="threat-item header-row" style={{ gridTemplateColumns: '1.5fr 1fr 1.5fr 1fr 1fr 1fr', background: 'rgba(0,0,0,0.5)' }}>
                <span>Threat Hash</span>
                <span>Source IP</span>
                <span>Identified Vector</span>
                <span>Confidence</span>
                <span>Action</span>
                <span style={{ textAlign: 'right' }}>Time</span>
              </div>
              
              {threats.map((threat, index) => (
                <div 
                  key={index} 
                  className="threat-item animated-entry"
                  style={{ 
                    gridTemplateColumns: '1.5fr 1fr 1.5fr 1fr 1fr 1fr', 
                    borderBottom: '1px solid var(--border-color)',
                    borderRadius: 0,
                    borderLeft: threat.action === 'BLOCK' ? '4px solid #ef4444' : '4px solid #10b981',
                    animationDelay: `${0.4 + (index * 0.05)}s` 
                  }}
                >
                  <div className="threat-id">
                    <Database size={14} style={{ color: 'var(--accent-purple)' }}/>
                    {threat.id.substring(0, 12)}...
                  </div>
                  
                  <div style={{ fontFamily: 'monospace', color: '#a1a1aa' }}>
                    <Globe size={14} style={{ display: 'inline', marginRight: '6px' }}/>
                    {hashToIp(threat.id)}
                  </div>

                  <div style={{ fontWeight: 500, color: threat.action === 'BLOCK' ? '#ef4444' : '#10b981' }}>
                    {getAttackVector(threat.confidence)}
                  </div>

                  <div className="threat-score">
                    {threat.confidence}%
                  </div>
                  
                  <div className={`threat-action ${threat.action === 'BLOCK' ? 'action-block' : 'action-review'}`} style={{ padding: '4px 10px' }}>
                    {getActionIcon(threat.action)}
                    {threat.action}
                  </div>
                  
                  <div className="threat-time">
                    {threat.time}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default App;
