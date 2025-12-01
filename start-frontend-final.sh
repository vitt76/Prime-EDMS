#!/bin/bash
echo "========================================="
echo "DAM Frontend - WSL Ubuntu Startup"
echo "========================================="

# Find project directory
if [ -d "/mnt/host/c/DAM/Prime-EDMS" ]; then
    PROJECT_ROOT="/mnt/host/c/DAM/Prime-EDMS"
elif [ -d "/mnt/c/DAM/Prime-EDMS" ]; then
    PROJECT_ROOT="/mnt/c/DAM/Prime-EDMS"
else
    echo "ERROR: Project directory not found!"
    exit 1
fi

cd "$PROJECT_ROOT"
echo "Project: $PROJECT_ROOT"

# Check Node.js
echo ""
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"

# Go to frontend
cd frontend
echo ""
echo "Installing dependencies..."
npm install

# Create .env.development if not exists
if [ ! -f ".env.development" ]; then
    echo "Creating .env.development..."
    cat > .env.development << 'EOF'
VITE_API_URL=
VITE_APP_TITLE=DAM System
VITE_DEBUG=true
EOF
fi

echo ""
echo "========================================="
echo "Starting Vite dev server..."
echo "Frontend will be available at:"
echo "  http://localhost:5173"
echo "  http://localhost:5173/login"
echo "========================================="
echo ""

npm run dev -- --host 0.0.0.0 --port 5173

