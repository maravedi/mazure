#!/bin/bash
# Run all tests and quality checks for mazure

set -e

echo "====================================="
echo "Mazure Test Suite"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check MongoDB
echo -e "${YELLOW}Checking MongoDB...${NC}"
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${RED}❌ MongoDB is not running${NC}"
    echo "Please start MongoDB: sudo systemctl start mongod"
    exit 1
fi
echo -e "${GREEN}✓ MongoDB is running${NC}"
echo ""

# Setup indexes
echo -e "${YELLOW}Setting up MongoDB indexes...${NC}"
python scripts/setup_mongodb_indexes.py
echo ""

# Run unit tests
echo -e "${YELLOW}Running unit tests...${NC}"
pytest tests/unit -v
echo ""

# Run integration tests
echo -e "${YELLOW}Running integration tests...${NC}"
pytest tests/integration -v
echo ""

# Run examples
echo -e "${YELLOW}Running examples...${NC}"
python examples/query_examples.py || echo -e "${YELLOW}(Examples may fail if no seeded data)${NC}"
echo ""

# Run benchmarks
echo -e "${YELLOW}Running benchmarks...${NC}"
python scripts/benchmark_queries.py || echo -e "${YELLOW}(Benchmarks may fail if no seeded data)${NC}"
echo ""

echo -e "${GREEN}====================================="
echo -e "All tests completed!${NC}"
echo -e "====================================="
