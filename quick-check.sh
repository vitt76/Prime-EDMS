#!/bin/bash
echo "🔍 Quick DAM System Check"
echo "========================"

# Check WSL
if [ -z "$WSL_DISTRO_NAME" ]; then
    echo "❌ Not in WSL Ubuntu!"
    exit 1
fi

# Check project directory
if [ -d "/mnt/host/c/DAM/Prime-EDMS" ]; then
    cd /mnt/host/c/DAM/Prime-EDMS
elif [ -d "/mnt/c/DAM/Prime-EDMS" ]; then
    cd /mnt/c/DAM/Prime-EDMS
else
    echo "❌ Project directory not found!"
    exit 1
fi

echo "✅ Project found at: $(pwd)"

# Check Docker containers
echo ""
echo "🐳 Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "❌ Docker not running"

# Check Node.js
echo ""
echo "🔍 Node.js:"
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
    echo "✅ npm: $(npm --version)"
else
    echo "❌ Node.js not installed"
fi

# Check URLs
echo ""
echo "🌐 URL checks:"
if curl -s --max-time 3 http://localhost:8080/ > /dev/null; then
    echo "✅ Backend: http://localhost:8080"
else
    echo "❌ Backend: http://localhost:8080"
fi

if curl -s --max-time 3 http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend: http://localhost:5173"
else
    echo "❌ Frontend: http://localhost:5173"
fi

echo ""
echo "🎯 Next steps:"
if ! curl -s --max-time 3 http://localhost:8080/ > /dev/null; then
    echo "   Run: ./start-system-wsl.sh"
fi
if ! curl -s --max-time 3 http://localhost:5173/ > /dev/null; then
    echo "   Run: ./start-frontend-wsl.sh"
fi
