#!/bin/bash
echo "🚀 Starting DAM System in Ubuntu WSL"
echo "===================================="

# Check if we're in WSL
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "❌ This script must be run in WSL Ubuntu!"
    echo "   Open WSL terminal: Press Win+R, type 'wsl', press Enter"
    exit 1
fi

echo "✅ Running in WSL: $WSL_DISTRO_NAME"

# Go to project directory
if [ -d "/mnt/host/c/DAM/Prime-EDMS" ]; then
    cd /mnt/host/c/DAM/Prime-EDMS
    PROJECT_PATH="/mnt/host/c/DAM/Prime-EDMS"
elif [ -d "/mnt/c/DAM/Prime-EDMS" ]; then
    cd /mnt/c/DAM/Prime-EDMS
    PROJECT_PATH="/mnt/c/DAM/Prime-EDMS"
else
    echo "❌ Project directory not found!"
    exit 1
fi

echo "📁 Project path: $PROJECT_PATH"

# Stop old containers
echo ""
echo "🛑 Stopping old containers..."
docker-compose down

# Start new containers
echo ""
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for containers
echo ""
echo "⏳ Waiting for containers to start..."
sleep 15

# Check status
echo ""
echo "📊 Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check Node.js
echo ""
echo "🔍 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Installing..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Make scripts executable
echo ""
echo "🔧 Setting up scripts..."
chmod +x *.sh

echo ""
echo "🎉 System is ready!"
echo ""
echo "🌐 URLs:"
echo "   Backend:  http://localhost:8080"
echo "   Frontend: http://localhost:5173 (after running frontend)"
echo ""
echo "🚀 To start frontend, run:"
echo "   ./start-frontend-wsl.sh"
echo ""
echo "📋 To check everything is working:"
echo "   ./diagnose-system.sh"
