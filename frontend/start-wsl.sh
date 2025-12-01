#!/bin/bash
echo "🚀 Starting DAM Frontend Dev Server in WSL Ubuntu..."
echo "📁 Changing to frontend directory..."
cd /mnt/c/DAM/Prime-EDMS/frontend

echo "📦 Installing dependencies..."
npm install

echo "🌐 Starting Vite dev server..."
npm run dev -- --host 0.0.0.0 --port 5173

echo "✅ Dev server should be running at http://localhost:5173"
echo "🌍 Open in browser: http://localhost:5173/login"
