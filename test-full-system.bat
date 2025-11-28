@echo off
echo ====================================
echo DAM System Full Test
echo ====================================
echo.

echo Step 1: Starting WSL Ubuntu...
echo.

wsl bash -c "
echo '=== WSL Ubuntu Test ==='
echo ''

# Find project directory
if [ -d '/mnt/host/c/DAM/Prime-EDMS' ]; then
    cd /mnt/host/c/DAM/Prime-EDMS
    PROJECT_PATH='/mnt/host/c/DAM/Prime-EDMS'
elif [ -d '/mnt/c/DAM/Prime-EDMS' ]; then
    cd /mnt/c/DAM/Prime-EDMS
    PROJECT_PATH='/mnt/c/DAM/Prime-EDMS'
else
    echo '❌ Project directory not found!'
    exit 1
fi

echo '📁 Project path: '$PROJECT_PATH
echo ''

echo '🐳 Starting Docker containers...'
docker-compose up -d 2>/dev/null

echo '⏳ Waiting for containers...'
sleep 15

echo ''
echo '📊 Docker containers:'
docker ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null || echo '❌ Docker not available'

echo ''
echo '🔍 Checking Node.js...'
if ! command -v node &> /dev/null; then
    echo '❌ Node.js not found! Installing...'
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - 2>/dev/null
    sudo apt-get install -y nodejs 2>/dev/null
fi

echo '✅ Node.js: '$(node --version 2>/dev/null || echo 'not found')
echo '✅ npm: '$(npm --version 2>/dev/null || echo 'not found')

echo ''
echo '📦 Installing frontend dependencies...'
cd frontend
npm install --silent 2>/dev/null || echo '❌ npm install failed'

echo ''
echo '🚀 Starting Vite dev server...'
timeout 30 npm run dev -- --host 0.0.0.0 --port 5173 2>&1 | head -20 &
DEV_PID=\$!

echo '⏳ Waiting for dev server...'
sleep 10

echo ''
echo '🌐 Testing URLs...'
echo 'Backend (http://localhost:8080):'
curl -s -I http://localhost:8080/ 2>/dev/null | head -1 || echo '❌ Backend not responding'

echo 'Frontend (http://localhost:5173):'
curl -s -I http://localhost:5173/ 2>/dev/null | head -1 || echo '❌ Frontend not responding'

echo 'Test page (http://localhost:5173/test.html):'
curl -s -I http://localhost:5173/test.html 2>/dev/null | head -1 || echo '❌ Test page not responding'

echo ''
echo '🧹 Cleaning up...'
kill \$DEV_PID 2>/dev/null

echo ''
echo '🎉 Test completed!'
echo ''
echo '📋 MANUAL TESTING:'
echo '1. Open browser to http://localhost:5173/login'
echo '2. Login with: admin@example.com / admin123'
echo '3. Should redirect to dashboard'
"

echo.
echo ====================================
echo Test completed! 
echo.
echo MANUAL TESTING REQUIRED:
echo 1. Open: http://localhost:5173/login
echo 2. Login: admin@example.com / admin123
echo 3. Should work now!
echo ====================================
echo.
pause
