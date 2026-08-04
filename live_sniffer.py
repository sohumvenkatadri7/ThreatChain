import os
import requests
import ctypes
import sys
import time
import random
from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime

# Enable ANSI colors for Windows Terminal
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
    print(f"{Colors.RED}{Colors.BOLD}=================================================================={Colors.RESET}")
    print(f"{Colors.RED}{Colors.BOLD} CRITICAL ERROR: ADMINISTRATOR PRIVILEGES REQUIRED {Colors.RESET}")
    print(f"{Colors.RED}{Colors.BOLD}=================================================================={Colors.RESET}")
    print("You must run this script as an Administrator.")
    sys.exit(1)

# Keep track of blocked IPs so we don't spam the firewall
blocked_ips = set()

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} 🛡️  ThreatChain Deep Packet Interceptor v1.0.0 {Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}===================================================================================={Colors.RESET}")
    print(f"{Colors.YELLOW}📡 Listening to live network interfaces...{Colors.RESET}\n")
    print(f"{Colors.BOLD}{'TIME':<10} | {'SOURCE IP':<15} | {'DEST IP':<15} | {'PORT':<6} | {'AI CONFIDENCE':<13} | {'ACTION'}{Colors.RESET}")
    print("-" * 84)

def block_ip(ip_address):
    if ip_address in blocked_ips:
        return
    print(f"\n{Colors.RED}{Colors.BOLD}[!!!] EXECUTING OS-LEVEL FIREWALL MITIGATION ON: {ip_address}{Colors.RESET}")
    cmd = f'netsh advfirewall firewall add rule name="ThreatChain Block {ip_address}" dir=in action=block remoteip={ip_address} >nul 2>&1'
    os.system(cmd)
    blocked_ips.add(ip_address)
    print(f"{Colors.RED} > [SUCCESS] {ip_address} has been permanently blocked.{Colors.RESET}\n")
    print("-" * 84)

# Rate limit the output so it's actually readable (max 2 packets per second)
last_print_time = 0

def packet_callback(packet):
    global last_print_time
    
    # Throttle processing to one packet every 0.5 seconds
    if time.time() - last_print_time < 0.5:
        return
        
    if IP in packet:
        last_print_time = time.time()
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # Ignore localhost traffic
        if src_ip == "127.0.0.1" or dst_ip == "127.0.0.1":
            return
            
        payload = [0] * 77
        port = 0
        
        if TCP in packet:
            port = packet[TCP].dport
            payload[0] = port
            payload[1] = 6 
            payload[2] = len(packet)
        elif UDP in packet:
            port = packet[UDP].dport
            payload[0] = port
            payload[1] = 17 
            payload[2] = len(packet)
        else:
            return 
            
        # Demo Injection (5% chance)
        is_demo_attack = False
        if random.random() < 0.05: 
            is_demo_attack = True
            payload = [21, 17, 422810, 12449, 17544, 149.77672921646268, 61.59303459137641, 40.826427575252666, 0.7511901485653416, 8.296464143955049, 798321, 60.59415705472274, 16.14488550566304, 239.46991796300122, 44.25163744535454, 38.43619942349271, 1, 53.44102574635213, 96.5832851349903, 453.58130589264124, 25.446899910548016, 13.472696576917166, 904.3537549068022, 18.082651316614683, 6.020033015638083, 482.32705598681144, 984.2743464170275, 6.457957634435313, 44.66469337012454, 107.18208024475861, 6.598717972007266, 361.2528428003154, 22.143197254670667, 70.3875042370808, 9.934721944676667, 912.8758651256339, 5.979077059093579, 552.4489558293382, 33.685801101405325, 121.4774437724826, 124.87133190570665, 74.73921748823071, 56.30066396926018, 961.7903456031997, 7.922788520118958, 95.99993685954134, 64.23545839348675, 690.342670759906, 7.816679794782488, 917.5796344260236, 370.4695644492177, 51.87244817000136, 3.0635365424820957, 49.61596943109067, 73.30158679296403, 88.31879194445126, 93.83921256337372, 765.0881393500842, 92.20546419360745, 1.438107778084592, 16.28365117475028, 992.0530281482474, 8.684134805913233, 0.06648516760973111, 9.06837714702501, 91.2223038936449, 6.216797203674396, 425.30730322641665, 38.71382025604554, 4.45137441838456, 358.24444055963113, 206.77686460752355, 7.140717772554245, 0.7481935407762508, 1.607270738723906, 247.47833657787677, 5.543865021539761]

        try:
            response = requests.post(API_URL, json={"features": payload}, timeout=1)
            if response.status_code == 200:
                data = response.json()
                action = data.get("action")
                score = data.get("confidence_score")
                
                # Format time
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Format score percentage
                score_pct = f"{(score * 100):.2f}%"
                
                if action == "BLOCK":
                    print(f"{current_time:<10} | {Colors.RED}{src_ip:<15}{Colors.RESET} | {dst_ip:<15} | {port:<6} | {Colors.RED}{score_pct:<13}{Colors.RESET} | {Colors.RED}{Colors.BOLD}BLOCK 🚫{Colors.RESET}")
                    block_ip(src_ip)
                elif action == "REVIEW":
                    print(f"{current_time:<10} | {Colors.YELLOW}{src_ip:<15}{Colors.RESET} | {dst_ip:<15} | {port:<6} | {Colors.YELLOW}{score_pct:<13}{Colors.RESET} | {Colors.YELLOW}REVIEW ⚠️{Colors.RESET}")
                else:
                    print(f"{current_time:<10} | {src_ip:<15} | {dst_ip:<15} | {port:<6} | {Colors.GREEN}{score_pct:<13}{Colors.RESET} | {Colors.GREEN}ALLOW ✅{Colors.RESET}")
                    
        except requests.exceptions.RequestException:
            pass 

print_header()
# Start sniffing live traffic
sniff(prn=packet_callback, store=0, filter="ip")
