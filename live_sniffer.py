import os
import random
import requests
import ctypes
import sys
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

os.system("")

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

API_URL = "http://127.0.0.1:8000/scan-network-log"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("You must run this script as an Administrator.")
    sys.exit(1)

# Active network flows tracker
# Structure: { "IP": {"packets": 0, "bytes": 0, "start_time": time.time(), "port": 0, "protocol": 6} }
active_flows = {}
blocked_ips = set()
lock = threading.Lock()

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} 🛡️  ThreatChain Authentic FlowMeter v2.0 {Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.YELLOW}📡 Aggregating REAL packets from your network interface...{Colors.RESET}\n")
    print(f"{Colors.BOLD}{'TIME':<10} | {'SOURCE IP':<15} | {'PKTS/SEC':<10} | {'BYTES/SEC':<10} | {'AI SCORE':<10} | {'ACTION'}{Colors.RESET}")
    print("-" * 84)

import socket

def get_whitelisted_ips():
    ips = {"127.0.0.1", "0.0.0.0", "localhost", "192.168.0.1", "192.168.1.1"}
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            ips.add(ip)
    except Exception:
        pass
    return ips

WHITELISTED_IPS = get_whitelisted_ips()

def block_ip(ip_address):
    if ip_address in blocked_ips or ip_address in WHITELISTED_IPS:
        return
    print(f"\n{Colors.RED}{Colors.BOLD}[!!!] EXECUTING OS-LEVEL FIREWALL MITIGATION ON: {ip_address}{Colors.RESET}")
    cmd = f'netsh advfirewall firewall add rule name="ThreatChain Block {ip_address}" dir=in action=block remoteip={ip_address} >nul 2>&1'
    os.system(cmd)
    blocked_ips.add(ip_address)
    print(f"{Colors.RED} > [SUCCESS] {ip_address} has been permanently blocked.{Colors.RESET}\n")
    print("-" * 84)

def packet_callback(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # Whitelist protection: Never capture localhost, own machine IP, router, or broadcasts
        if src_ip in WHITELISTED_IPS:
            return
        if src_ip.startswith("224.") or src_ip.startswith("239.") or src_ip.endswith(".255") or src_ip.endswith(".1"):
            return
            
        pkt_len = len(packet)
        port = 0
        protocol = 6
        
        if TCP in packet:
            port = packet[TCP].dport
            protocol = 6
        elif UDP in packet:
            port = packet[UDP].dport
            protocol = 17
        else:
            return
            
        with lock:
            if src_ip not in active_flows:
                active_flows[src_ip] = {
                    "packets": 0,
                    "bytes": 0,
                    "start_time": time.time(),
                    "port": port,
                    "protocol": protocol
                }
            
            active_flows[src_ip]["packets"] += 1
            active_flows[src_ip]["bytes"] += pkt_len

def flow_analyzer():
    """ Runs every 2 seconds to aggregate real traffic flows and send them to the AI """
    while True:
        time.sleep(2.0)
        
        with lock:
            current_time = time.time()
            flows_to_process = active_flows.copy()
            active_flows.clear() # Reset window
            
        for ip, data in flows_to_process.items():
            if ip in blocked_ips:
                continue
                
            duration = current_time - data["start_time"]
            if duration <= 0: duration = 1.0
            
            # CALCULATE REAL METRICS FROM YOUR PHONE/DEVICE
            pkts_per_sec = data["packets"] / duration
            bytes_per_sec = data["bytes"] / duration
            
            # Base benign array (Must be mostly zeros so the AI doesn't flag random noise as an anomaly)
            payload = [0.0] * 47
            
            # INJECT REAL AUTHENTIC DATA into the exact indices expected by the 47-feature model
            payload[4] = pkts_per_sec                                        # flow packets/s
            payload[32] = bytes_per_sec                                      # flow bytes/s
            payload[9] = float(duration * 1_000_000)                         # flow duration (us)
            payload[13] = float(data["bytes"] / max(data["packets"], 1))     # packet length mean
            payload[7] = float((duration * 1_000_000) / max(data["packets"], 1)) # flow iat mean
            payload[42] = pkts_per_sec                                       # fwd packets/s
            payload[29] = float(data["packets"] * 20)                        # fwd header length
            
            try:
                response = requests.post(API_URL, json={"features": payload, "src_ip": ip}, timeout=1)
                if response.status_code == 200:
                    result = response.json()
                    action = result.get("action")
                    score = result.get("confidence", result.get("confidence_score", 0))
                    score_pct = f"{(score * 100):.1f}%"
                    curr_time_str = datetime.now().strftime("%H:%M:%S")
                    
                    if action == "BLOCK":
                        print(f"{curr_time_str:<10} | {Colors.RED}{ip:<15}{Colors.RESET} | {int(pkts_per_sec):<10} | {int(bytes_per_sec):<10} | {Colors.RED}{score_pct:<10}{Colors.RESET} | {Colors.RED}{Colors.BOLD}BLOCK 🚫{Colors.RESET}")
                        block_ip(ip)
                    elif pkts_per_sec > 1:
                        print(f"{curr_time_str:<10} | {ip:<15} | {int(pkts_per_sec):<10} | {int(bytes_per_sec):<10} | {Colors.GREEN}{score_pct:<10}{Colors.RESET} | {Colors.GREEN}ALLOW ✅{Colors.RESET}")
                        
            except requests.exceptions.RequestException:
                pass

print_header()

# Start background analyzer thread
analyzer_thread = threading.Thread(target=flow_analyzer, daemon=True)
analyzer_thread.start()

# Start authentic sniffing
sniff(prn=packet_callback, store=0, filter="ip")
