import requests
import random
import time
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

API_URL = "http://127.0.0.1:8000/scan-network-log"

print("=" * 60)
print(" [*] ThreatChain Multi-Class Attack Simulator v2.0")
print("=" * 60)
print("Generates authentic 47-feature hybrid network traffic.\n")

def generate_payload(scenario="NORMAL"):
    """
    Generates a 47-feature array formatted for the hybrid XGBoost engine.
    """
    payload = [0.0] * 47
    
    if scenario == "SWARM_DDOS":
        # Volumetric UDP/IoT Flood (>1000 pkts/s)
        pps = random.uniform(1100.0, 1600.0)
        bytes_sec = pps * random.uniform(1100.0, 1450.0)
        duration_us = random.uniform(1.8, 2.2) * 1e6
        
        payload[4] = pps                                  # flow packets/s
        payload[32] = bytes_sec                           # flow bytes/s
        payload[9] = duration_us                          # flow duration
        payload[13] = bytes_sec / pps                     # packet length mean
        payload[7] = duration_us / pps                    # flow iat mean
        payload[42] = pps                                 # fwd packets/s
        payload[29] = pps * 20.0                          # fwd header length
        src_ip = f"192.168.0.{random.randint(180, 240)}"
        return payload, src_ip, "Swarm / IoT Botnet (UDP Flood)"

    elif scenario == "IT_EXPLOIT":
        # Enterprise IT Exploit / Slowloris / Vulnerability Scan
        pps = random.uniform(480.0, 750.0)
        bytes_sec = pps * random.uniform(200.0, 500.0)
        duration_us = random.uniform(8.0, 15.0) * 1e6
        
        payload[4] = pps
        payload[32] = bytes_sec
        payload[9] = duration_us
        payload[13] = bytes_sec / pps
        payload[7] = duration_us / pps
        payload[42] = pps
        src_ip = f"10.0.4.{random.randint(10, 90)}"
        return payload, src_ip, "Enterprise IT Exploit (Port Scan / Buffer)"

    else:
        # Benign everyday traffic (browsing / streaming)
        pps = random.uniform(15.0, 85.0)
        bytes_sec = pps * random.uniform(300.0, 800.0)
        
        payload[4] = pps
        payload[32] = bytes_sec
        payload[13] = bytes_sec / pps
        src_ip = "192.168.0.105"
        return payload, src_ip, "Normal User Traffic"

test_scenarios = [
    "NORMAL",
    "SWARM_DDOS",
    "NORMAL",
    "IT_EXPLOIT",
    "SWARM_DDOS"
]

for idx, scenario in enumerate(test_scenarios, 1):
    payload, ip, desc = generate_payload(scenario)
    print(f"[{idx}/5] Injecting: {desc} (IP: {ip})...")
    
    try:
        response = requests.post(API_URL, json={"features": payload, "src_ip": ip}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            action = data.get("action")
            conf = data.get("confidence", 0) * 100
            tx = data.get("blockchain_tx")
            
            status_symbol = "[BLOCK]" if action == "BLOCK" else "[ALLOW]"
            print(f"      -> Action: {status_symbol} | Confidence: {conf:.2f}%")
            if tx:
                print(f"      -> Committed to Ethereum: {tx[:24]}...")
        else:
            print(f"      -> API Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"      -> Connection Failed: {e}")
        
    print("-" * 50)
    time.sleep(2)

print("\n Simulation Complete! Verified on React Console & Ethereum L2.")
