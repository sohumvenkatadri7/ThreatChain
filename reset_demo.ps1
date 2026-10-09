# ThreatChain 1-Click Demo Reset & Firewall Purge Script
# Run in Administrator PowerShell to restore pristine demo state

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 🛡️  ThreatChain Demo Reset & Firewall Rule Purge" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Clean up all Windows Firewall rules created by ThreatChain
Write-Host "`n[*] Purging ThreatChain firewall blacklist rules..." -ForegroundColor Yellow

$rules = netsh advfirewall firewall show rule name=all | Select-String "ThreatChain"
$count = 0

if ($rules) {
    # Delete all specific ThreatChain rules
    netsh advfirewall firewall delete rule name="ThreatChain Block 192.168.0.1" >$null 2>&1
    netsh advfirewall firewall delete rule name="ThreatChain Block 192.168.0.179" >$null 2>&1
    netsh advfirewall firewall delete rule name="ThreatChain Block 192.168.0.224" >$null 2>&1
    
    # Generic loop to remove any remaining ThreatChain rules
    netsh advfirewall firewall show rule name=all | Select-String "Rule Name:\s+(ThreatChain.*)" | ForEach-Object {
        $ruleName = $_.Matches.Groups[1].Value.Trim()
        Write-Host "  -> Removing rule: $ruleName" -ForegroundColor DarkGray
        netsh advfirewall firewall delete rule name="$ruleName" >$null 2>&1
        $count++
    }
    Write-Host "✅ Purged $count ThreatChain firewall rules successfully!" -ForegroundColor Green
} else {
    Write-Host "✅ No stale ThreatChain firewall rules found." -ForegroundColor Green
}

# 2. Verify Hardhat Node & Blockchain connection
Write-Host "`n[*] Verifying Ethereum Hardhat Blockchain..." -ForegroundColor Yellow
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8545" -Method Post -Body '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' -ContentType "application/json" -TimeoutSec 2
    $blockHex = $res.result
    $blockDec = [Convert]::ToInt32($blockHex, 16)
    Write-Host "✅ Hardhat L2 is running! Current Block Height: #$blockDec" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Hardhat node (http://127.0.0.1:8545) is not running!" -ForegroundColor Red
    Write-Host "   Start it with: cd threatchain-contracts; npx hardhat node" -ForegroundColor Red
}

# 3. Verify FastAPI Backend
Write-Host "`n[*] Verifying ThreatChain AI API Server..." -ForegroundColor Yellow
try {
    $apiRes = Invoke-RestMethod -Uri "http://127.0.0.1:8000/docs" -Method Get -TimeoutSec 2
    Write-Host "✅ FastAPI AI Gatekeeper is running at http://127.0.0.1:8000" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: FastAPI backend is not running!" -ForegroundColor Red
    Write-Host "   Start it with: cd threatchain-backend; python -m uvicorn main:app --reload" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " 🚀 System Clean & Ready for Live Pitch Demo!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
