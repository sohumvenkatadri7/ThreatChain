# 🛡️ ThreatChain: Demo Payloads

These payloads are pre-calculated to trigger specific Confidence Scores in your XGBoost model. 
During your presentation, copy the entire JSON block and paste it into the Swagger UI (`http://127.0.0.1:8000/docs`) under the `/scan-network-log` endpoint.

---

### 🟢 Payload 1: Normal Employee Traffic (Action: ALLOW)
**AI Confidence:** `~0.68%`
**Description:** Simulates normal web browsing (Port 80/TCP). No anomalies detected.
```json
{
  "features": [
    80, 6, 120, 5, 5, 100.0, 50.0, 10.0, 0.5, 2.0, 
    5000, 10.0, 2.0, 50.0, 10.0, 5.0, 0, 10.0, 20.0, 100.0, 
    5.0, 2.0, 200.0, 5.0, 2.0, 100.0, 200.0, 2.0, 10.0, 20.0, 
    2.0, 50.0, 5.0, 10.0, 2.0, 200.0, 2.0, 100.0, 10.0, 50.0, 
    50.0, 20.0, 10.0, 200.0, 2.0, 20.0, 10.0, 100.0, 2.0, 200.0, 
    100.0, 10.0, 1.0, 10.0, 20.0, 20.0, 20.0, 200.0, 20.0, 0.5, 
    5.0, 200.0, 2.0, 0.01, 2.0, 20.0, 2.0, 100.0, 10.0, 1.0, 
    100.0, 50.0, 2.0, 0.5, 0.5, 100.0, 2.0
  ]
}
```

---

### 🔴 Payload 2: FTP Brute Force Attack (Action: BLOCK)
**AI Confidence:** `~96.67%`
**Description:** Simulates an attacker trying to brute-force a file server (Port 21). Triggers high variance in forward packet metrics.
```json
{
  "features": [
    21, 6, 422810, 12449, 17544, 149.7, 61.5, 40.8, 0.7, 8.2, 
    798321, 60.5, 16.1, 239.4, 44.2, 38.4, 1, 53.4, 96.5, 453.5, 
    25.4, 13.4, 904.3, 18.0, 6.0, 482.3, 984.2, 6.4, 44.6, 107.1, 
    6.5, 361.2, 22.1, 70.3, 9.9, 912.8, 5.9, 552.4, 33.6, 121.4, 
    124.8, 74.7, 56.3, 961.7, 7.9, 95.9, 64.2, 690.3, 7.8, 917.5, 
    370.4, 51.8, 3.0, 49.6, 73.3, 88.3, 93.8, 765.0, 92.2, 1.4, 
    16.2, 992.0, 8.6, 0.06, 9.0, 91.2, 6.2, 425.3, 38.7, 4.4, 
    358.2, 206.7, 7.1, 0.7, 1.6, 247.4, 5.5
  ]
}
```

---

### 🔴 Payload 3: High-Volume DDoS Attack (Action: BLOCK)
**AI Confidence:** `~98.82%`
**Description:** Simulates a massive DDoS attack on Port 80. Packet sizes and Flow Bytes/s (Index 10) are completely saturated, breaking the model's threshold.
```json
{
  "features": [
    80, 17, 800000, 50000, 80000, 149.7, 61.5, 40.8, 0.7, 8.2, 
    999999, 60.5, 16.1, 239.4, 44.2, 38.4, 1, 53.4, 96.5, 453.5, 
    25.4, 13.4, 904.3, 18.0, 6.0, 482.3, 984.2, 6.4, 44.6, 107.1, 
    6.5, 361.2, 22.1, 70.3, 9.9, 912.8, 5.9, 552.4, 33.6, 121.4, 
    124.8, 74.7, 56.3, 961.7, 7.9, 95.9, 64.2, 690.3, 7.8, 917.5, 
    370.4, 51.8, 3.0, 49.6, 73.3, 88.3, 93.8, 765.0, 92.2, 1.4, 
    16.2, 992.0, 8.6, 0.06, 9.0, 91.2, 6.2, 425.3, 38.7, 4.4, 
    358.2, 206.7, 7.1, 0.7, 1.6, 247.4, 5.5
  ]
}
```
