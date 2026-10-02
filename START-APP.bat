@echo off
title OneSpace Personal Command Center
echo ===================================================
echo Starting OneSpace Full-Stack Application...
echo API and Frontend UI will be available at: http://localhost:5000
echo ===================================================
cd /d "%~dp0OneSpace_Phase1\server"
node src/server.js
pause
