@echo off
title ThreatChain Decommissioner
color 0c

echo ======================================================================
echo          THREATCHAIN AUTONOMOUS SOC - CLEAN SHUTDOWN
echo ======================================================================
echo.

:: Check for Administrative Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting Administrator privileges to purge firewall rules...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb runAs"
    exit /b
)

echo [*] Stopping background ThreatChain processes...

:: Terminate uvicorn / python processes running ThreatChain
taskkill /f /fi "WINDOWTITLE eq [ThreatChain]*" >nul 2>&1

:: Stop node processes on port 8545 (Hardhat) and 5173 (Vite)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8545" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [*] Purging any active firewall blacklist rules...
powershell -ExecutionPolicy Bypass -File "E:\ThreatChain\reset_demo.ps1" >nul 2>&1

echo.
echo ======================================================================
echo   [SUCCESS] All ThreatChain nodes, API, and UI cleanly shutdown!
echo ======================================================================
timeout /t 3 >nul
exit /b
