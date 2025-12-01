#!/bin/bash
echo "🔍 DAM System Diagnostic Tool"
echo "=============================="
echo ""

# Check if running in WSL
echo "1. WSL Environment Check:"
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "❌ NOT running in WSL Ubuntu!"
    echo "   Please run this script in Ubuntu WSL terminal, not PowerShell"
    echo "   Open WSL: Press Win+R, type 'wsl', press Enter"
    exit 1
else
    echo "✅ Running in WSL: $WSL_DISTRO_NAME"
fi

# Check Windows mount
echo "   Windows mount check:"
if [ ! -d "/mnt/c" ]; then
    echo "❌ Windows drives not mounted! (/mnt/c not found)"
    echo "   Try: sudo mount -t drvfs C: /mnt/c"
else
    echo "✅ Windows drives mounted (/mnt/c exists)"
fi
echo ""

# Check Node.js
echo "2. Node.js Check:"
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo "   Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "✅ Node.js: $NODE_VERSION"
    echo "✅ npm: $NPM_VERSION"
fi
echo ""

# Check directory structure
echo "3. Project Structure Check:"

# Try to find project directory
PROJECT_FOUND=false
if [ -d "/mnt/c/DAM/Prime-EDMS" ]; then
    cd /mnt/c/DAM/Prime-EDMS
    PROJECT_FOUND=true
    echo "✅ Found project at: /mnt/c/DAM/Prime-EDMS"
elif [ -d "/mnt/host/c/DAM/Prime-EDMS" ]; then
    cd /mnt/host/c/DAM/Prime-EDMS
    PROJECT_FOUND=true
    echo "✅ Found project at: /mnt/host/c/DAM/Prime-EDMS"
else
    echo "❌ Project directory not found!"
    echo "   Checked: /mnt/c/DAM/Prime-EDMS"
    echo "   Checked: /mnt/host/c/DAM/Prime-EDMS"
    echo "   Available mounts:"
    ls /mnt/
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ frontend directory not found!"
    exit 1
else
    echo "✅ frontend directory exists"
fi

if [ ! -f "frontend/package.json" ]; then
    echo "❌ package.json not found!"
    exit 1
else
    echo "✅ package.json exists"
fi
echo ""

# Check Docker
echo "4. Docker Check:"
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "   Please install Docker in WSL"
    exit 1
else
    DOCKER_VERSION=$(docker --version)
    echo "✅ $DOCKER_VERSION"
fi

# Check running containers
echo "   Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check network connectivity
echo "5. Network Connectivity Check:"
echo "   Testing localhost:8080 (Backend)..."
if curl -s --max-time 5 http://localhost:8080/ > /dev/null; then
    echo "✅ Backend accessible on localhost:8080"
else
    echo "❌ Backend NOT accessible on localhost:8080"
fi

echo "   Testing localhost:5173 (Frontend)..."
if curl -s --max-time 5 http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend accessible on localhost:5173"
else
    echo "❌ Frontend NOT accessible on localhost:5173"
fi
echo ""

# Check frontend setup
echo "6. Frontend Setup Check:"
cd frontend

echo "   Checking node_modules..."
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found! Running npm install..."
    npm install
else
    echo "✅ node_modules exists"
fi

echo "   Checking if dev server can start..."
timeout 10s npm run dev -- --port 5173 --host 127.0.0.1 > dev-server-test.log 2>&1 &
DEV_PID=$!
sleep 3

if kill -0 $DEV_PID 2>/dev/null; then
    echo "✅ Dev server process started successfully"
    kill $DEV_PID
else
    echo "❌ Dev server failed to start"
    echo "   Check dev-server-test.log for errors:"
    cat dev-server-test.log
fi

cd ..
echo ""

# Summary
echo "7. Summary:"
echo "   - WSL Environment: $([ -n "$WSL_DISTRO_NAME" ] && echo "✅ OK" || echo "❌ FAIL")"
echo "   - Node.js: $(command -v node >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FAIL")"
echo "   - npm: $(command -v npm >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FAIL")"
echo "   - Project Structure: $([ -d "frontend" ] && [ -f "frontend/package.json" ] && echo "✅ OK" || echo "❌ FAIL")"
echo "   - Docker: $(command -v docker >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FAIL")"
echo "   - Backend Access: $(curl -s --max-time 5 http://localhost:8080/ >/dev/null && echo "✅ OK" || echo "❌ FAIL")"
echo "   - Frontend Access: $(curl -s --max-time 5 http://localhost:5173/ >/dev/null && echo "✅ OK" || echo "❌ FAIL")"
echo ""

echo "🎯 Recommendations:"
if ! curl -s --max-time 5 http://localhost:5173/ >/dev/null; then
    echo "   1. Try running: ./start-frontend-wsl.sh"
    echo "   2. Check if port 5173 is available: netstat -tlnp | grep :5173"
    echo "   3. Try different host: npm run dev -- --host localhost --port 5173"
fi

echo ""
echo "📋 Logs saved to: frontend/dev-server-test.log"
