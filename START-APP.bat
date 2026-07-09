@echo off
title GLO E-Lottery - Ticket Verifier
cd /d "%~dp0backend"
echo(
echo  ============================================
echo    GLO E-Lottery - starting the app
echo  ============================================
echo(

REM check Node
node --version >nul 2>&1
if errorlevel 1 (
  echo  [!] Node.js is not installed.
  echo      Install Node 22+ from https://nodejs.org  then run this again.
  echo(
  pause
  exit /b
)

REM install deps once
if not exist "node_modules" (
  echo  [1/3] Installing dependencies ^(first run only^)...
  call npm install
)

REM seed database once
if not exist "db\glo.db" (
  echo  [2/3] Creating database with sample tickets...
  call npm run seed
)

echo  [3/3] Starting server at http://localhost:8080
echo(
echo  Opening the app in your browser...
start "" "http://localhost:8080"
echo  Keep this window open while using the app. Close it to stop.
echo(
node server.js
pause
