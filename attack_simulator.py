import requests
import random
import time

API_URL = "http://127.0.0.1:8000/scan-network-log"

print("=========================================")
print(" ThreatChain Attack Simulator Started... ")
print("=========================================\n")

def generate_payload(is_malicious):
    """
    Generates a 77-feature array.
    We tweak a few key features that a tree-based model trained on CIC-IDS2018 
    would likely pick up as an anomaly (like high packet sizes, port anomalies, etc.)
    """
    # Start with a baseline normal-looking payload
    payload = [0] * 77
    
    # Assign some random realistic normal values
    payload[0] = random.randint(20, 80)      # e.g. Port
    payload[1] = random.randint(6, 17)       # Protocol
    payload[2] = random.randint(100, 500)    # Flow duration
    
    if is_malicious:
        # This payload was generated to trigger exactly 96.6% confidence on this specific model
        payload = [21, 17, 422810, 12449, 17544, 149.77672921646268, 61.59303459137641, 40.826427575252666, 0.7511901485653416, 8.296464143955049, 798321, 60.59415705472274, 16.14488550566304, 239.46991796300122, 44.25163744535454, 38.43619942349271, 1, 53.44102574635213, 96.5832851349903, 453.58130589264124, 25.446899910548016, 13.472696576917166, 904.3537549068022, 18.082651316614683, 6.020033015638083, 482.32705598681144, 984.2743464170275, 6.457957634435313, 44.66469337012454, 107.18208024475861, 6.598717972007266, 361.2528428003154, 22.143197254670667, 70.3875042370808, 9.934721944676667, 912.8758651256339, 5.979077059093579, 552.4489558293382, 33.685801101405325, 121.4774437724826, 124.87133190570665, 74.73921748823071, 56.30066396926018, 961.7903456031997, 7.922788520118958, 95.99993685954134, 64.23545839348675, 690.342670759906, 7.816679794782488, 917.5796344260236, 370.4695644492177, 51.87244817000136, 3.0635365424820957, 49.61596943109067, 73.30158679296403, 88.31879194445126, 93.83921256337372, 765.0881393500842, 92.20546419360745, 1.438107778084592, 16.28365117475028, 992.0530281482474, 8.684134805913233, 0.06648516760973111, 9.06837714702501, 91.2223038936449, 6.216797203674396, 425.30730322641665, 38.71382025604554, 4.45137441838456, 358.24444055963113, 206.77686460752355, 7.140717772554245, 0.7481935407762508, 1.607270738723906, 247.47833657787677, 5.543865021539761]
        
    return {"features": payload}

# Send 5 test payloads
for i in range(1, 6):
    # Randomly decide if this packet is an attack (40% chance)
    is_attack = random.random() < 0.4
    packet_type = "MALICIOUS" if is_attack else "BENIGN"
    
    print(f"[{i}/5] Sending {packet_type} traffic payload to API...")
    
    payload = generate_payload(is_malicious=is_attack)
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   -> AI Confidence: {data['confidence_score']}")
            print(f"   -> Action Taken: {data['action']}")
            if data['blockchain_tx']:
                print(f"   -> Blockchain Tx: {data['blockchain_tx']}")
        else:
            print(f"   -> Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   -> Connection Failed. Is the backend running? ({e})")
        
    print("-" * 40)
    time.sleep(2) # Pause for 2 seconds so you can watch the frontend update

print("\nSimulation Complete! Check your React Dashboard.")
