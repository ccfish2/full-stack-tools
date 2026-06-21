#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Statsig Application - Docker Compose${NC}"
echo -e "${GREEN}================================${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Building Docker images...${NC}"
docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build complete${NC}\n"

echo -e "${YELLOW}2. Starting services...${NC}"
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to start services${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Services started${NC}\n"

# Wait for services to be ready
echo -e "${YELLOW}3. Waiting for services to be ready...${NC}"
sleep 10

# Check if backend is responding
echo -e "${YELLOW}4. Checking backend status...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/hello/ > /dev/null; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✓ All services are running!${NC}"
echo -e "${GREEN}================================${NC}\n"

echo -e "${YELLOW}Access the application at:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:9090${NC}"
echo -e "  Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "  Database: ${GREEN}localhost:5432${NC}\n"

echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs: ${GREEN}docker-compose logs -f${NC}"
echo -e "  Stop services: ${GREEN}docker-compose down${NC}"
echo -e "  Stop and clean: ${GREEN}docker-compose down -v${NC}\n"

echo -e "${YELLOW}To interact with services:${NC}"
echo -e "  Backend shell: ${GREEN}docker-compose exec backend bash${NC}"
echo -e "  Database: ${GREEN}docker-compose exec db psql -U postgres -d statsig_db${NC}"
echo -e "  Frontend shell: ${GREEN}docker-compose exec frontend bash${NC}\n"
