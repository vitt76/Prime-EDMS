#!/bin/bash
echo "🐧 Starting DAM Frontend in WSL Ubuntu"
echo "======================================="

# Check if we're in WSL
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "❌ Not running in WSL Ubuntu!"
    exit 1
fi

echo "✅ Running in WSL: $WSL_DISTRO_NAME"

# Go to project directory
# Try different mount paths for WSL
if [ -d "/mnt/c/DAM/Prime-EDMS/frontend" ]; then
    cd /mnt/c/DAM/Prime-EDMS/frontend
elif [ -d "/mnt/host/c/DAM/Prime-EDMS/frontend" ]; then
    cd /mnt/host/c/DAM/Prime-EDMS/frontend
else
    echo "❌ Cannot find project directory!"
    echo "   Tried: /mnt/c/DAM/Prime-EDMS/frontend"
    echo "   Tried: /mnt/host/c/DAM/Prime-EDMS/frontend"
    echo "   Current WSL mount paths:"
    ls /mnt/
    exit 1
fi
echo "📁 Changed to: $(pwd)"

# Check Node.js
echo "🔍 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Installing..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

node --version
npm --version

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Start dev server
echo "🚀 Starting Vite dev server..."
echo "🌐 Will be available at: http://localhost:5173"
echo "🔗 Test login at: http://localhost:5173/login"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev -- --host 0.0.0.0 --port 5173
