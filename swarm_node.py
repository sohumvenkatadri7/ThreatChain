import os
import time
import ctypes
import sys
from web3 import Web3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("You must run this script as an Administrator for firewall mitigation.")
    sys.exit(1)

# --- WEB3 BLOCKCHAIN SETUP ---
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

if not w3.is_connected():
    print(f"{Colors.RED}[!] Could not connect to Hardhat node. Is it running?{Colors.RESET}")
    sys.exit(1)

def get_contract_address(default="0x5FbDB2315678afecb367f032d93F642f64180aa3"):
    val = os.getenv("CONTRACT_ADDRESS")
    if val:
        return val
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, ".env"),
        os.path.join(base_dir, "..", ".env"),
        os.path.join(base_dir, "threatchain-frontend", ".env")
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("CONTRACT_ADDRESS=") or line.startswith("VITE_CONTRACT_ADDRESS="):
                        addr = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if addr:
                            return addr
    return default

# Loaded dynamically from .env with fallback
CONTRACT_ADDRESS = get_contract_address()

# ABI containing both the Event and the Function so we can decode the input
CONTRACT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "threatId", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "confidence", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "actionTaken", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "ThreatAnchored",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_threatId", "type": "string"},
            {"internalType": "uint256", "name": "_confidence", "type": "uint256"},
            {"internalType": "string", "name": "_actionTaken", "type": "string"}
        ],
        "name": "logThreat",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

blocked_ips = set()

def block_ip(ip_address):
    if ip_address in blocked_ips or ip_address == "Unknown":
        return
    print(f"\n{Colors.RED}{Colors.BOLD}[!!!] SWARM INTELLIGENCE TRIGGERED: PREEMPTIVE MITIGATION {Colors.RESET}")
    print(f"{Colors.YELLOW} > Applying OS-Level Firewall rule to block {ip_address}{Colors.RESET}")
    
    # Execute the Windows firewall block command
    cmd = f'netsh advfirewall firewall add rule name="ThreatChain Swarm Block {ip_address}" dir=in action=block remoteip={ip_address} >nul 2>&1'
    os.system(cmd)
    
    blocked_ips.add(ip_address)
    print(f"{Colors.GREEN} > [SUCCESS] {ip_address} is now blocked across the Swarm.{Colors.RESET}\n")

def handle_raw_log(log):
    try:
        # Fetch the original transaction that triggered this log
        tx_hash = log['transactionHash']
        tx = w3.eth.get_transaction(tx_hash)
        
        # Decode the function arguments passed to logThreat
        func_obj, func_params = contract.decode_function_input(tx['input'])
        
        threat_id = func_params.get('_threatId', '')
        action = func_params.get('_actionTaken', '')
        
        # In main.py, we encoded threatId as "192.168.1.5-a1b2c3d4"
        if "-" in threat_id:
            attacker_ip = threat_id.split("-")[0]
            
            print(f"\n{Colors.CYAN}[*] Blockchain Event Received! Global Threat ID: {threat_id}{Colors.RESET}")
            
            if action == "BLOCK":
                print(f"{Colors.RED}[!] Threat was blocked by Node A. Replicating rule on Node B...{Colors.RESET}")
                block_ip(attacker_ip)
    except Exception as e:
        print(f"[!] Error decoding transaction: {e}")

def listen_for_threats():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} 🌐 ThreatChain Decentralized Swarm Node (Node B) {Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.YELLOW}📡 Connected to Ethereum Ledger. Waiting for global threat intelligence...{Colors.RESET}\n")
    
    last_processed_block = w3.eth.block_number
    
    while True:
        try:
            current_block = w3.eth.block_number
            if current_block > last_processed_block:
                # Use raw get_logs to avoid Web3.py's broken indexed-string decoder
                raw_logs = w3.eth.get_logs({
                    "fromBlock": last_processed_block + 1,
                    "toBlock": current_block,
                    "address": w3.to_checksum_address(CONTRACT_ADDRESS)
                })
                
                for log in raw_logs:
                    handle_raw_log(log)
                    
                last_processed_block = current_block
            time.sleep(2)
        except Exception as e:
            print(f"[!] Error reading blockchain: {e}")
            time.sleep(5)

if __name__ == "__main__":
    listen_for_threats()
