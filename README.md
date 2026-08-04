# 🛡️ ThreatChain AI-SOC
> **An Enterprise-Grade, Blockchain-Anchored Network Security Platform.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.x-cyan.svg)
![Solidity](https://img.shields.io/badge/solidity-^0.8.0-black.svg)

ThreatChain is a next-generation Security Operations Center (SOC) that combines **Machine Learning (XGBoost)** for zero-day threat detection with **Blockchain Smart Contracts** for immutable audit trails. When an attack is detected, the AI calculates a confidence score, physically mitigates the threat at the OS level, and permanently anchors the cryptographic hash of the attack to the Ethereum blockchain.

---

## ✨ Core Features
*   🧠 **AI Inference Engine:** Utilizes an XGBoost model trained on the CIC-IDS2018 dataset to evaluate 77 distinct network flow features in real-time.
*   ⛓️ **Immutable Audit Trails:** Drops the "Black Box" AI problem by hashing malicious payloads (SHA-256) and anchoring them to a Solidity Smart Contract, proving the exact state of the network at the time of mitigation.
*   🛡️ **Autonomous Mitigation:** Python-based micro-FlowMeter detects high-velocity attacks (like UDP/TCP Floods) and physically alters the Windows Defender Firewall to drop the attacker's IP.
*   📊 **Glassmorphism React Dashboard:** A sleek, movie-hacker aesthetic UI that parses blockchain hashes into readable IP addresses and visualizes real-time network drops with pulse animations.

---

## 🏗️ Architecture

1.  **Network Layer (Scapy):** `live_sniffer.py` acts as a micro-FlowMeter, aggregating packets per second and bytes per second over a 2-second sliding window.
2.  **API Layer (FastAPI):** Receives the 77-feature array, invokes the XGBoost model, and calculates the AI Confidence Score.
3.  **Blockchain Layer (Hardhat):** If confidence > 90.0%, the backend triggers an `ethers.js` call to `ThreatChainVault.sol` to anchor the threat.
4.  **Presentation Layer (React):** Listens for the `ThreatAnchored` event on the blockchain and updates the UI dynamically.

---

## 🚀 How to Run the Project

### 1. Start the Blockchain (Terminal 1)
```bash
cd E:\ThreatChain\threatchain-contracts
npx hardhat node
```
*(Keep this running. It simulates a local Ethereum network).*

### 2. Start the AI Backend (Terminal 2)
```bash
cd E:\ThreatChain\threatchain-backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*(The backend is now ready to receive packets and interact with the blockchain).*

### 3. Start the React Dashboard (Terminal 3)
```bash
cd E:\ThreatChain\threatchain-frontend
npm run dev
```
*(Open `http://localhost:5173` in your browser).*

### 4. Start the Micro-FlowMeter (Terminal 4 - MUST BE ADMINISTRATOR)
Open a new **PowerShell** window as **Administrator**:
```bash
cd E:\ThreatChain
.\threatchain-backend\venv\Scripts\python.exe live_sniffer.py
```
*(The sniffer is now actively monitoring your PC's network interface).*

---

## 💥 How to Run the Live Demo (Phone Attack)

To prove the system works organically without faking payloads, you can launch a real DDoS simulation from your smartphone.

1. Ensure your phone and PC are on the same Wi-Fi network.
2. Install **Termux** on your Android device.
3. Run this exact one-line command in Termux (Replace `YOUR_PC_IP` with your PC's actual IPv4 address):

```bash
python -c "import socket; target='YOUR_PC_IP'; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); exec('while True:\n try: s.sendto(b\'DDoS_PAYLOAD_X\'*100, (target, 8000))\n except Exception: pass')"
```

**What happens next?**
*   Your phone will blast thousands of packets per second.
*   `live_sniffer.py` will catch the velocity spike.
*   The AI will score it at `98.8%`.
*   Windows Firewall will physically ban your phone's IP.
*   The React Dashboard will flash red and log the attack permanently to the blockchain!

*(To unblock your phone after the demo, run `netsh advfirewall firewall delete rule name="ThreatChain Block <YOUR_PHONE_IP>"` in an Administrator PowerShell).*

---
*Built for the future of decentralized cybersecurity.*
