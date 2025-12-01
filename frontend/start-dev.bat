@echo off
echo Starting DAM Frontend Dev Server...
cd /d C:\DAM\Prime-EDMS\frontend
npm run dev -- --port 3000 --host 0.0.0.0
pause
