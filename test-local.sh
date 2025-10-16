#!/bin/bash

echo "==========================================="
echo "RAG Knowledge Graph - Local Testing"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Neo4j is running
echo -e "${YELLOW}1. Checking Neo4j...${NC}"
if docker ps | grep -q neo4j; then
    echo -e "${GREEN}✓ Neo4j is running${NC}"
else
    echo -e "${YELLOW}Starting Neo4j...${NC}"
    docker run -d --name neo4j \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password \
        neo4j:latest
    echo -e "${GREEN}✓ Neo4j started${NC}"
    echo "Waiting for Neo4j to be ready..."
    sleep 15
fi

# Check if backend is running
echo ""
echo -e "${YELLOW}2. Checking Backend API...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo ""
    echo "Start backend in another terminal:"
    echo "  cd $(pwd)"
    echo "  python3 rag_api_server.py"
    echo ""
fi

# Check if frontend is running
echo ""
echo -e "${YELLOW}3. Checking Frontend...${NC}"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo ""
    echo "Start frontend in another terminal:"
    echo "  cd $(pwd)/frontend"
    echo "  npm start"
    echo ""
fi

echo ""
echo "==========================================="
echo "Access Points:"
echo "==========================================="
echo "Frontend:      http://localhost:3000"
echo "Backend API:   http://localhost:8000"
echo "Neo4j Browser: http://localhost:7474"
echo ""
echo "Test the system:"
echo "1. Open http://localhost:3000"
echo "2. Go to Build Graph tab"
echo "3. Enter your PostgreSQL connection string"
echo "4. Build the graph"
echo "5. Go to Chat tab and query!"
echo ""

