from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
import numpy as np
import uvicorn
from web3 import Web3
import hashlib

# Initialize the FastAPI app
app = FastAPI(title="ThreatChain AI Bridge", version="1.0")

# Enable CORS for the future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WEB3 BLOCKCHAIN SETUP ---
WEB3_PROVIDER_URL = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
CONTRACT_ABI = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_threatId",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_confidence",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_actionTaken",
				"type": "string"
			}
		],
		"name": "logThreat",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "string",
				"name": "threatId",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "confidence",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "actionTaken",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "ThreatAnchored",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "admin",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAllThreats",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "threatId",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "confidence",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "actionTaken",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct ThreatChainVault.ThreatLog[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getTotalThreatCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# Initialize contract (lazily evaluates connection on request)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Global variable to hold the loaded model
model_bundle = None
xgb_model = None

@app.on_event("startup")
def load_model():
    """Loads the exported joblib model bundle when the server starts."""
    global model_bundle, xgb_model
    try:
        print("[*] Booting up ThreatChain AI Core...")
        model_bundle = joblib.load("threathchain_xgboost.joblib")
        xgb_model = model_bundle['model']
        print("[*] Model loaded successfully and ready for inference.")
    except Exception as e:
        print(f"[!] Critical Error loading model: {e}")

# Define the expected JSON payload format
class NetworkLog(BaseModel):
    # For the MVP, we accept a list of 77 numeric features matching the dataset
    features: List[float]

@app.post("/scan-network-log")
def scan_network_log(log: NetworkLog):
    """
    Receives network flow data, predicts the threat probability, 
    applies the gatekeeper logic, and anchors critical threats to the blockchain.
    """
    if xgb_model is None:
        raise HTTPException(status_code=500, detail="AI Model is offline.")
    
    # 1. Convert the incoming list into a 2D numpy array for XGBoost
    try:
        input_data = np.array(log.features).reshape(1, -1)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")

    # 2. Run Inference
    try:
        # predict_proba returns [[prob_class_0, prob_class_1]]
        probabilities = xgb_model.predict_proba(input_data)
        malicious_prob = float(probabilities[0][1])  # Probability of being an attack
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    # 3. Adaptive Confidence Gatekeeper Logic
    threshold = 0.90
    
    if malicious_prob >= threshold:
        status = "CRITICAL THREAT: Automatic Mitigation Triggered"
        action = "BLOCK"
    elif malicious_prob > 0.50:
        status = "POTENTIAL THREAT: Routed for Manual SOC Review"
        action = "REVIEW"
    else:
        status = "NORMAL TRAFFIC: No Anomalies Detected"
        action = "ALLOW"

    # 4. Blockchain Anchoring for Critical/Review Threats
    tx_hash = None
    if action in ["BLOCK", "REVIEW"] and contract:
        try:
            payload_string = ''.join(map(str, log.features))
            threat_id = hashlib.sha256(payload_string.encode()).hexdigest()[:16]
            scaled_confidence = int(malicious_prob * 10000)
            
            account = w3.eth.accounts[0]
            tx_hash = contract.functions.logThreat(
                threat_id, scaled_confidence, action
            ).transact({'from': account})
            tx_hash = w3.to_hex(tx_hash)
        except Exception as blockchain_err:
            print(f"[!] Blockchain anchoring warning: {blockchain_err}")

    # 5. Return the standardized JSON response
    return {
        "status": "success",
        "confidence_score": round(malicious_prob, 4),
        "threat_status": status,
        "action": action,
        "blockchain_tx": tx_hash
    }