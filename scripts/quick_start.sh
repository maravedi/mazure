#!/bin/bash
# Quick start script for mazure with discovery integration

set -e

echo "====================================="
echo "Mazure Quick Start"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Setting up MongoDB indexes...${NC}"
python scripts/setup_mongodb_indexes.py
echo -e "${GREEN}✓ Indexes created${NC}"
echo ""

echo -e "${YELLOW}Step 2: Starting mazure server...${NC}"
echo "Starting on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn mazure.app:app --reload --port 8000
