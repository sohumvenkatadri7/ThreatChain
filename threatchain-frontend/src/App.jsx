import { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { Shield, ShieldAlert, ShieldCheck, Activity, Database, Clock, Fingerprint } from 'lucide-react';
import ThreatChainVaultABI from './ThreatChainVaultABI.json';
import './index.css';

// Using the local Hardhat deployment address
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const RPC_URL = "http://127.0.0.1:8545";

function App() {
  const [threats, setThreats] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    connectToBlockchain();
  }, []);

  const connectToBlockchain = async () => {
    try {
      // Connect to the local Hardhat node
      const provider = new ethers.JsonRpcProvider(RPC_URL);
      
      // Test connection
      await provider.getNetwork();
      setIsConnected(true);

      // Initialize Contract
      const contract = new ethers.Contract(CONTRACT_ADDRESS, ThreatChainVaultABI, provider);

      // Fetch initial threats
      fetchThreats(contract);

      // Listen for real-time events from the AI Backend!
      contract.on("ThreatAnchored", (threatId, confidence, actionTaken, timestamp) => {
        console.log("New Threat Anchored:", threatId);
        // Refresh the list when a new threat arrives
        fetchThreats(contract);
      });

    } catch (err) {
      console.error("Failed to connect to local blockchain. Is Hardhat running?", err);
      setIsConnected(false);
      setLoading(false);
    }
  };

  const fetchThreats = async (contract) => {
    try {
      const data = await contract.getAllThreats();
      
      // Parse the blockchain tuple into a clean JS array
      const parsedThreats = data.map(t => ({
        id: t.threatId,
        // Confidence is stored as score * 10000 on chain, convert back to percentage
        confidence: (Number(t.confidence) / 100).toFixed(2),
        action: t.actionTaken,
        // Convert Unix timestamp to local readable time
        time: new Date(Number(t.timestamp) * 1000).toLocaleString()
      }));

      // Sort newest first
      parsedThreats.sort((a, b) => new Date(b.time) - new Date(a.time));
      
      setThreats(parsedThreats);
    } catch (error) {
      console.error("Error fetching threats:", error);
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
    <div className="dashboard-container">
      <header className="header animated-entry" style={{ animationDelay: '0.1s' }}>
        <div className="logo-container">
          <Database size={32} className="logo-icon" />
          <h1>ThreatChain SOC</h1>
        </div>
        <div className="connection-status">
          <div className={`status-dot ${isConnected ? 'connected' : ''}`}></div>
          {isConnected ? 'Vault Connected' : 'Vault Offline'}
        </div>
      </header>

      <div className="stats-grid animated-entry" style={{ animationDelay: '0.2s' }}>
        <div className="glass-panel stat-card">
          <span className="stat-title"><Activity size={18} /> Total Intercepts</span>
          <span className="stat-value">{threats.length}</span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-title"><ShieldAlert size={18} /> Critical Blocks</span>
          <span className="stat-value" style={{ color: '#ef4444' }}>
            {threats.filter(t => t.action === 'BLOCK').length}
          </span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-title"><Shield size={18} /> Pending Reviews</span>
          <span className="stat-value" style={{ color: '#f59e0b' }}>
            {threats.filter(t => t.action === 'REVIEW').length}
          </span>
        </div>
      </div>

      <section className="threats-section animated-entry" style={{ animationDelay: '0.3s' }}>
        <h2><Fingerprint size={24} /> Immutable Threat Logs</h2>
        
        <div className="glass-panel">
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
            <div className="threat-list">
              <div className="threat-item header-row">
                <span>Threat Hash (SHA-256)</span>
                <span>AI Confidence</span>
                <span>Mitigation Action</span>
                <span style={{ textAlign: 'right' }}>Timestamp</span>
              </div>
              
              {threats.map((threat, index) => (
                <div 
                  key={index} 
                  className="threat-item animated-entry"
                  style={{ animationDelay: `${0.4 + (index * 0.1)}s` }}
                >
                  <div className="threat-id">
                    <Fingerprint size={16} />
                    {threat.id.substring(0, 16)}...
                  </div>
                  <div className="threat-score">
                    {threat.confidence}%
                  </div>
                  <div className={`threat-action ${threat.action === 'BLOCK' ? 'action-block' : 'action-review'}`}>
                    {getActionIcon(threat.action)}
                    {threat.action}
                  </div>
                  <div className="threat-time">
                    <Clock size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom' }} />
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
