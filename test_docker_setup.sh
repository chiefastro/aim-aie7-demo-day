#!/bin/bash

# ACP Demo - Docker Setup Test (Shell Script Version)
# This script provides a simpler alternative to the Python test script

set -e

echo "🚀 ACP Demo - Docker Setup Test (Shell Version)"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    echo -n "  Testing $service_name... "
    
    if curl -s --max-time 5 "http://localhost:$port$endpoint" >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

# Function to check port accessibility
check_port() {
    local port=$1
    local service_name=$2
    
    echo -n "  Port $port ($service_name)... "
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

# Check Docker status
echo -e "\n${BLUE}🐳 Checking Docker container status...${NC}"
if command_exists docker-compose; then
    if docker-compose ps | grep -q "Up"; then
        echo -e "  ${GREEN}Docker containers are running${NC}"
    else
        echo -e "  ${YELLOW}No Docker containers are running${NC}"
    fi
else
    echo -e "  ${RED}docker-compose not found${NC}"
fi

# Check ports
echo -e "\n${BLUE}🔌 Checking port accessibility...${NC}"
healthy_services=0
total_services=4

if check_port 6333 "Qdrant"; then ((healthy_services++)); fi
if check_port 3001 "GOR API"; then ((healthy_services++)); fi
if check_port 3002 "MCP Server"; then ((healthy_services++)); fi
if check_port 3000 "Offer Scraper"; then ((healthy_services++)); fi

# Check service health (if ports are accessible)
echo -e "\n${BLUE}🏥 Testing service health...${NC}"
if check_port 6333 "Qdrant" >/dev/null; then
    check_service "Qdrant" 6333 "/health"
fi

if check_port 3001 "GOR API" >/dev/null; then
    check_service "GOR API" 3001 "/health"
fi

if check_port 3002 "MCP Server" >/dev/null; then
    # MCP server might not have a health endpoint, so just check if it's listening
    echo -e "  MCP Server: ${GREEN}✅ (listening)${NC}"
fi

if check_port 3000 "Offer Scraper" >/dev/null; then
    check_service "Offer Scraper" 3000 "/demo"
fi

# Print summary
echo -e "\n${BLUE}==================================================${NC}"
echo -e "${BLUE}📊 DOCKER SETUP TEST SUMMARY${NC}"
echo -e "${BLUE}==================================================${NC}"

echo -e "🏥 Service Health: ${healthy_services}/${total_services} accessible"

# Recommendations
echo -e "\n${BLUE}💡 Recommendations:${NC}"

if [ $healthy_services -eq $total_services ]; then
    echo -e "  ${GREEN}🎉 All services are accessible! You can now run the demo.${NC}"
    echo -e "  ${GREEN}🚀 Try: make cli${NC}"
elif [ $healthy_services -gt 0 ]; then
    echo -e "  ${YELLOW}⚠️  Some services are not accessible. Check logs with: make logs${NC}"
    echo -e "  ${YELLOW}🔄 Try restarting: make down && make up${NC}"
else
    echo -e "  ${RED}❌ No services are accessible. Check if Docker is running.${NC}"
    echo -e "  ${RED}🚀 Try starting fresh: make start${NC}"
fi

echo -e "\n${BLUE}📚 Useful commands:${NC}"
echo -e "  make help     - Show all available commands"
echo -e "  make status   - Check service status"
echo -e "  make logs     - View service logs"
echo -e "  make clean    - Clean up everything"
echo -e "  make reset    - Reset and start fresh"

# Exit with appropriate code
if [ $healthy_services -eq $total_services ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Docker setup is working correctly.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  $((total_services - healthy_services)) service(s) have issues.${NC}"
    exit 1
fi
