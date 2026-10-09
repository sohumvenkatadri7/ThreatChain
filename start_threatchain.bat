@echo off
title ThreatChain Master Launcher
color 0b

echo ======================================================================
echo          THREATCHAIN AUTONOMOUS SOC - MASTER LAUNCHER v2.0
echo ======================================================================
echo.

:: 1. Check for Administrative Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb runAs"
    exit /b
)

cd /d "E:\ThreatChain"

echo [*] Administrator privileges confirmed.
echo [*] Step 1/6: Purging stale firewall rules...
powershell -ExecutionPolicy Bypass -File "E:\ThreatChain\reset_demo.ps1" >nul 2>&1

echo [*] Step 2/6: Starting Ethereum Hardhat L2 Node (Port 8545)...
start "[ThreatChain] 1. Ethereum L2 Blockchain" cmd /k "cd /d E:\ThreatChain\threatchain-contracts && npx hardhat node --hostname 0.0.0.0"

:: Give Hardhat 4 seconds to boot before deploying contract
timeout /t 4 /nobreak >nul

echo [*] Step 3/6: Deploying Smart Contract and Synchronizing .env...
cd /d "E:\ThreatChain\threatchain-contracts"
call npx hardhat run scripts/deploy.js --network localhost
cd /d "E:\ThreatChain"

echo [*] Step 4/6: Launching FastAPI AI Gatekeeper (Port 8000)...
start "[ThreatChain] 2. AI Gatekeeper (FastAPI)" cmd /k "cd /d E:\ThreatChain\threatchain-backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo [*] Step 5/6: Launching React SOC Dashboard (Port 5173)...
start "[ThreatChain] 3. React SOC Dashboard" cmd /k "cd /d E:\ThreatChain\threatchain-frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo [*] Step 6/6: Starting Swarm Node B & Live Sniffer Node A...
start "[ThreatChain] 4. Swarm Node B Defender" cmd /k "cd /d E:\ThreatChain && python swarm_node.py"
start "[ThreatChain] 5. Live Sniffer Node A" cmd /k "cd /d E:\ThreatChain && python live_sniffer.py"

:: Open default browser to React Dashboard
timeout /t 2 /nobreak >nul
echo.
echo ======================================================================
echo   [SUCCESS] Entire ThreatChain Ecosystem Online!
echo   Opening Security Operations Center in default browser...
echo ======================================================================
start http://localhost:5173

exit /b
