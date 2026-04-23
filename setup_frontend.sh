#!/bin/bash
# ============================================================================
# Frontend Setup Script for AI-IDS Dashboard
# Muhammad Abdul Rahman (B01821977)
# ============================================================================

echo "========================================================================"
echo "  AI-IDS DASHBOARD - FRONTEND SETUP"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create frontend directory structure
echo -e "${BLUE}[STEP 1] Creating frontend directory structure...${NC}"

mkdir -p frontend/src
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/services

echo -e "${GREEN}✅ Directory structure created${NC}"
echo ""

# Step 2: Copy files to correct locations
echo -e "${BLUE}[STEP 2] Setting up frontend files...${NC}"

# Copy package.json
cp frontend_package.json frontend/package.json

# Copy React files
cp frontend_App.js frontend/src/App.js
cp frontend_index.js frontend/src/index.js
cp frontend_index.css frontend/src/index.css

# Copy HTML
cp frontend_public_index.html frontend/public/index.html

echo -e "${GREEN}✅ Files copied to frontend/{ directory${NC}"
echo ""

# Step 3: Navigate and install
echo -e "${BLUE}[STEP 3] Installing npm packages...${NC}"
echo -e "${YELLOW}This may take 2-3 minutes...${NC}"
echo ""

cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found!${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    echo "Recommended version: 18.x or higher"
    exit 1
fi

echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"
echo ""

# Install dependencies
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All packages installed successfully!${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Some packages failed to install${NC}"
    echo "Try running: cd frontend && npm install"
    exit 1
fi

echo ""
echo "========================================================================"
echo -e "  ${GREEN}FRONTEND SETUP COMPLETE! 🎉${NC}"
echo "========================================================================"
echo ""
echo -e "${BLUE}To start the dashboard:${NC}"
echo ""
echo "  cd frontend"
echo "  npm start"
echo ""
echo -e "${BLUE}Dashboard will open at:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}Note:${NC} Make sure the backend API is running on port 8000!"
echo "  python main_api.py"
echo ""
echo "========================================================================"
