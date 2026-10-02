@echo off
title OneSpace Dev Server Launcher
echo Starting Backend API and Vite Frontend via CMD...
start "OneSpace API Server" cmd /k "cd /d "%~dp0OneSpace_Phase1\server" && node src/server.js"
start "OneSpace Vite Frontend" cmd /k "cd /d "%~dp0OneSpace_Phase1" && npx vite"
