import sys
import os
import requests
from web3 import Web3

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=" * 65)
print(" [*] ThreatChain Pre-Flight Diagnostic Health Check")
print("=" * 65)

all_ok = True

# 1. Check Hardhat Node
print("\n[1/4] Checking Ethereum Hardhat Node (port 8545)...")
try:
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if w3.is_connected():
        block = w3.eth.block_number
        print(f"  [+] Hardhat L2 Connected! Current Block: #{block}")
    else:
        print("  [-] Hardhat node is not responding at http://127.0.0.1:8545")
        all_ok = False
except Exception as e:
    print(f"  [-] Hardhat error: {e}")
    all_ok = False

# 2. Check Smart Contract Deployment
print("\n[2/4] Checking Smart Contract Deployment...")
contract_addr = None
env_files = [".env", "threatchain-frontend/.env", "threatchain-backend/.env"]
for env_file in env_files:
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("CONTRACT_ADDRESS=") or line.startswith("VITE_CONTRACT_ADDRESS="):
                    contract_addr = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
        if contract_addr:
            break

if not contract_addr:
    contract_addr = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

try:
    code = w3.eth.get_code(w3.to_checksum_address(contract_addr))
    if len(code) > 0:
        print(f"  [+] Contract deployed at: {contract_addr} (Bytecode size: {len(code)} bytes)")
    else:
        print(f"  [-] Contract at {contract_addr} has 0 bytecode! Run deploy.js first.")
        all_ok = False
except Exception as e:
    print(f"  [-] Contract check error: {e}")
    all_ok = False

# 3. Check FastAPI AI Backend
print("\n[3/4] Checking FastAPI AI Backend (port 8000)...")
try:
    res = requests.get("http://127.0.0.1:8000/docs", timeout=2)
    if res.status_code == 200:
        print("  [+] FastAPI AI Gatekeeper is Online at http://127.0.0.1:8000")
    else:
        print(f"  [-] FastAPI returned status code: {res.status_code}")
        all_ok = False
except Exception as e:
    print(f"  [-] FastAPI backend offline: {e}")
    all_ok = False

# 4. Check End-to-End Inference & Dynamic Confidence
print("\n[4/4] Testing End-to-End AI Inference Pipeline...")
try:
    # Test normal traffic
    payload_normal = [0.0] * 47
    payload_normal[4] = 60.0
    res_normal = requests.post("http://127.0.0.1:8000/scan-network-log", json={"features": payload_normal, "src_ip": "127.0.0.2"}, timeout=2)
    data_normal = res_normal.json()
    
    # Test attack traffic
    payload_attack = [0.0] * 47
    payload_attack[4] = 1200.0
    payload_attack[32] = 1200.0 * 1200
    res_attack = requests.post("http://127.0.0.1:8000/scan-network-log", json={"features": payload_attack, "src_ip": "192.168.0.224"}, timeout=3)
    data_attack = res_attack.json()
    
    if data_normal.get("action") == "ALLOW" and data_attack.get("action") == "BLOCK":
        print(f"  [+] Normal Traffic (60 pkts/s) -> ALLOW (Confidence: {data_normal.get('confidence')*100:.1f}%)")
        print(f"  [+] Attack Traffic (1200 pkts/s) -> BLOCK (Confidence: {data_attack.get('confidence')*100:.2f}%)")
        tx = data_attack.get('blockchain_tx', 'None')
        if tx:
            print(f"  [+] Ethereum TxHash Generated: {tx[:20]}...")
    else:
        print(f"  [-] Unexpected response: Normal={data_normal.get('action')}, Attack={data_attack.get('action')}")
        all_ok = False
except Exception as e:
    print(f"  [-] Inference test failed: {e}")
    all_ok = False

print("\n" + "=" * 65)
if all_ok:
    print(" [SUCCESS] ALL SYSTEMS GO! ThreatChain is fully primed for live demo.")
else:
    print(" [WARNING] SOME CHECKS FAILED. Please review the errors above.")
print("=" * 65)
