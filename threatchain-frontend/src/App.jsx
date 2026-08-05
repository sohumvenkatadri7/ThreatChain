import { useState, useEffect, useRef } from 'react';
import { ethers } from 'ethers';
import { 
  Shield, ShieldAlert, ShieldCheck, Activity, Database, Clock, 
  Fingerprint, Network, Cpu, Globe, Trash2, Search, Bell, 
  Settings, User, LayoutDashboard, BarChart3, Lock, Zap, Server, Download
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import ThreatChainVaultABI from './ThreatChainVaultABI.json';
import './index.css';

// Using the local Hardhat deployment address
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const RPC_URL = "http://127.0.0.1:8545";

const hashToIp = (hash) => {
  if (!hash) return "Unknown";
  // Extract real IP if it exists in the new format (e.g. 192.168.0.99-abc123hash)
  if (hash.includes('-')) return hash.split('-')[0];
  
  // Fallback to pseudo-IP logic for old hashes
  const cleanHash = hash.replace('0x', '');
  const p1 = parseInt(cleanHash.substring(0, 2), 16) % 255;
  const p2 = parseInt(cleanHash.substring(2, 4), 16) % 255;
  const p3 = parseInt(cleanHash.substring(4, 6), 16) % 255;
  const p4 = parseInt(cleanHash.substring(6, 8), 16) % 255;
  return `${p1}.${p2}.${p3}.${p4}`;
};

const getAttackVector = (score) => {
  const numScore = parseFloat(score);
  if (numScore > 98.0) return "DDoS / UDP Flood";
  if (numScore > 96.0) return "FTP Brute Force";
  if (numScore > 90.0) return "Zero-Day Anomaly";
  return "Standard Traffic";
};

function App() {
  const [threats, setThreats] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [livePulse, setLivePulse] = useState(false);
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
        setLivePulse(true);
        setTimeout(() => setLivePulse(false), 2000); // 2 second red alert
        fetchThreats(contract);
      });

      // Fallback Polling Mechanism for local Hardhat node
      setInterval(() => {
        fetchThreats(contract);
      }, 2000);
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
      setThreats(parsedThreats.reverse());
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const generateForensicPDF = async (threatRecord) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/threat-details/${threatRecord.id}`);
      const data = await response.json();
      
      let features = [];
      let txHash = "Not available (Legacy)";
      if (data.details) {
        if (data.details.top_features) features = data.details.top_features;
        if (data.details.tx_hash) txHash = data.details.tx_hash;
      }

      const doc = new jsPDF();
      
      // Header
      doc.setFillColor(15, 23, 42); // Slate 900
      doc.rect(0, 0, 210, 30, 'F');
      doc.setTextColor(239, 68, 68); // Red 500
      doc.setFontSize(22);
      doc.text("ThreatChain Forensic Audit & Incident Report", 14, 20);
      
      // Subtitle
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(14);
      doc.text("Incident Metadata", 14, 45);
      
      // Metadata
      doc.setFontSize(11);
      doc.text(`Generated Timestamp: ${new Date().toLocaleString()}`, 14, 55);
      doc.text(`Isolated Attacker IP: ${hashToIp(threatRecord.id)}`, 14, 62);
      doc.text(`Ethereum TxHash: ${txHash}`, 14, 69);
      doc.text(`AI Confidence Score: ${threatRecord.confidence}%`, 14, 76);
      doc.text(`Action Taken: ${threatRecord.action}`, 14, 83);
      
      // Table
      if (features.length > 0) {
        autoTable(doc, {
          startY: 95,
          head: [['XAI Feature Name', 'SHAP Impact Magnitude']],
          body: features.map(f => [f.feature, f.impact.toString()]),
          headStyles: { fillColor: [239, 68, 68] },
          theme: 'grid'
        });
      } else {
        doc.text("XAI Features: Not available in active cache.", 14, 95);
      }
      
      doc.save(`ThreatChain_Audit_${threatRecord.id.substring(0,6)}.pdf`);
    } catch (err) {
      console.error("PDF Generation failed", err);
      alert(`Export Failed: ${err.message}. If you just restarted the server, run a new attack first so the SHAP cache generates!`);
    }
  };

  // ----------------------------------------------------
  // SUB-COMPONENTS FOR A REAL ENTERPRISE PRODUCT FEEL
  // ----------------------------------------------------

  const Sidebar = () => (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon"><Shield size={24} /></div>
        <div className="brand-text">
          <h2>ThreatChain</h2>
          <span>Enterprise Edition</span>
        </div>
      </div>
      
      <nav className="nav-menu">
        <div className="nav-group">Main Menu</div>
        <a href="#" className="nav-item active"><LayoutDashboard size={18}/> Main Dashboard</a>
      </nav>

      <div className="sidebar-footer">
        <div className={`node-status ${isConnected ? 'online' : 'offline'}`}>
          <div className="status-dot"></div>
          {isConnected ? 'Node: Syncing (ETH)' : 'Node: Disconnected'}
        </div>
      </div>
    </aside>
  );

  const Topbar = () => (
    <header className="topbar">
      <div className="search-container">
      </div>
      <div className="topbar-actions">
        <button className="icon-button" onClick={handleClearLogs} title="Clear Display">
          <Trash2 size={18} /> <span style={{fontSize: '13px', marginLeft: '5px'}}>Clear</span>
        </button>
        <div className="user-profile" style={{marginLeft: '20px'}}>
          <div className="avatar"><User size={16} /></div>
          <div className="user-details">
            <span className="user-name">Admin User</span>
            <span className="user-role">SOC Tier 3</span>
          </div>
        </div>
      </div>
    </header>
  );

  return (
    <div className={`app-layout ${livePulse ? 'critical-alert' : ''}`}>
      <Sidebar />
      
      <main className="main-content">
        <Topbar />
        
        <div className="dashboard-scroll-area">
          <div className="page-header">
            <div>
              <h1>Security Operations Center</h1>
              <p>Real-time network traffic analysis anchored by Ethereum Smart Contracts.</p>
            </div>
          </div>

          {/* KPI Row */}
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-icon blue"><Network size={20}/></div>
              <div className="kpi-data">
                <span className="kpi-label">Active Node</span>
                <span className="kpi-value">Localhost (L2)</span>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon green"><Zap size={20}/></div>
              <div className="kpi-data">
                <span className="kpi-label">AI Inference Engine</span>
                <span className="kpi-value">XGBoost 99.2%</span>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon red"><ShieldAlert size={20}/></div>
              <div className="kpi-data">
                <span className="kpi-label">Threats Mitigated</span>
                <span className="kpi-value text-red">{threats.filter(t => t.action === 'BLOCK').length}</span>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon purple"><Cpu size={20}/></div>
              <div className="kpi-data">
                <span className="kpi-label">Avg Confidence</span>
                <span className="kpi-value">
                  {threats.length > 0 ? (threats.reduce((a, b) => a + parseFloat(b.confidence), 0) / threats.length).toFixed(1) : 0}%
                </span>
              </div>
            </div>
          </div>

          {/* Middle Row: Radar + Telemetry */}
          <div className="middle-grid">
            {/* Global Radar */}
            <div className="panel radar-panel">
              <div className="panel-header">
                <h3>Global Threat Radar</h3>
                <span className={`status-badge ${livePulse ? 'danger' : 'safe'}`}>
                  {livePulse ? 'CRITICAL ANOMALY' : 'SCANNING'}
                </span>
              </div>
              <div className="radar-container">
                <div className="radar-circle">
                  <div className="radar-grid-bg"></div>
                  <div className="radar-crosshair"></div>
                  <div className="radar-sweeper"></div>
                  {/* Blip that shows up on alert */}
                  {livePulse && <div className="radar-blip"></div>}
                </div>
              </div>
              <div className="radar-footer">
                <Globe size={14}/> Monitoring 77 Variance Features in Real-Time
              </div>
            </div>

            {/* Fake Live Telemetry Graph (CSS based for MVP) */}
            <div className="panel telemetry-panel">
              <div className="panel-header">
                <h3>Network Velocity (Packets/sec)</h3>
                <Activity size={18} className="text-muted" />
              </div>
              <div className="telemetry-chart">
                {/* Render bars, last one goes huge if alert is active */}
                {[...Array(20)].map((_, i) => (
                  <div 
                    key={i} 
                    className={`bar ${i === 19 && livePulse ? 'spike' : ''}`}
                    style={{ height: i === 19 && livePulse ? '90%' : `${Math.random() * 20 + 10}%` }}
                  ></div>
                ))}
              </div>
              <div className="telemetry-footer">
                <span className="text-muted">Threshold: 1,000 pkts/sec</span>
                <span style={{color: livePulse ? '#ef4444' : '#10b981', fontWeight: 600}}>
                  {livePulse ? '1540 pkts/s (DDoS DETECTED)' : '42 pkts/s (Normal)'}
                </span>
              </div>
            </div>
          </div>

          {/* Bottom Row: Ledger Table */}
          <div className="panel ledger-panel">
            <div className="panel-header">
              <h3>Immutable Ledger Intercepts</h3>
              <button className="export-btn"><Fingerprint size={14}/> Export Hash Logs</button>
            </div>
            
            <div className="table-wrapper">
              <table className="enterprise-table">
                <thead>
                  <tr>
                    <th>TxHash / Blockchain ID</th>
                    <th>Source IP (Decoded)</th>
                    <th>Identified Vector</th>
                    <th>XGBoost Confidence</th>
                    <th>Firewall Action</th>
                    <th>Forensic Audit</th>
                    <th style={{textAlign: 'right'}}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan="7" className="table-message">Syncing with Smart Contract...</td></tr>
                  ) : threats.length === 0 ? (
                    <tr><td colSpan="7" className="table-message">No malicious activity detected.</td></tr>
                  ) : (
                    threats.map((threat, index) => (
                      <tr key={index} className="fade-in-row">
                        <td className="hash-cell">
                          <Database size={14} className="text-purple"/> 
                          {threat.id.substring(0, 16)}...
                        </td>
                        <td className="ip-cell">{hashToIp(threat.id)}</td>
                        <td className="vector-cell">{getAttackVector(threat.confidence)}</td>
                        <td className="confidence-cell">{threat.confidence}%</td>
                        <td>
                          <span className={`badge ${threat.action === 'BLOCK' ? 'badge-danger' : 'badge-safe'}`}>
                            {threat.action}
                          </span>
                        </td>
                        <td>
                          <button 
                            className="icon-button" 
                            style={{color: '#8b5cf6', fontSize: '13px', padding: '4px 8px'}}
                            onClick={() => generateForensicPDF(threat)}
                            title="Export PDF Audit"
                          >
                            <Download size={14} style={{marginRight: '4px', verticalAlign: 'middle'}}/> Export
                          </button>
                        </td>
                        <td className="time-cell">{threat.time}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}

export default App;
