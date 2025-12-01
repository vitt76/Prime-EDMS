@echo off
echo Opening WSL Ubuntu and running DAM system setup...
echo.

wsl bash -c "
echo '=== WSL Ubuntu Terminal ==='
echo 'Setting up DAM System...'
echo ''

# Check if we're in project directory
if [ -d '/mnt/host/c/DAM/Prime-EDMS' ]; then
    cd /mnt/host/c/DAM/Prime-EDMS
    echo '✅ Project found at: /mnt/host/c/DAM/Prime-EDMS'
elif [ -d '/mnt/c/DAM/Prime-EDMS' ]; then
    cd /mnt/c/DAM/Prime-EDMS
    echo '✅ Project found at: /mnt/c/DAM/Prime-EDMS'
else
    echo '❌ Project directory not found!'
    echo 'Available mounts:'
    ls /mnt/
    exit 1
fi

echo ''
echo '🐳 Starting Docker containers...'
docker-compose up -d

echo ''
echo '⏳ Waiting for containers...'
sleep 10

echo ''
echo '📊 Container status:'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ''
echo '🔍 Checking Node.js...'
if ! command -v node &> /dev/null; then
    echo '❌ Node.js not found! Installing...'
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo '✅ Node.js:' $(node --version)
echo '✅ npm:' $(npm --version)

echo ''
echo '📦 Installing frontend dependencies...'
cd frontend
npm install
cd ..

echo ''
echo '🎉 System is ready!'
echo ''
echo '🌐 URLs:'
echo '   Backend:  http://localhost:8080'
echo '   Frontend: http://localhost:5173 (run: npm run dev)'
echo ''
echo '🚀 To start frontend:'
echo '   cd frontend && npm run dev -- --host 0.0.0.0 --port 5173'
"

echo.
echo Press any key to exit...
pause > nul
