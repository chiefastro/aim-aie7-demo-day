#!/bin/bash

# Restaurant A2A Demo Startup Script
# This script starts all components needed for the restaurant A2A demo

set -e

echo "🚀 Starting Restaurant A2A Demo..."
echo "=================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        exit 1
    fi
}

# Check ports
echo "🔍 Checking ports..."
check_port 8001
check_port 8002
check_port 8003
check_port 4001
check_port 4002
check_port 4003
check_port 3000
echo "✅ All ports are available"

# Function to start services in background
start_service() {
    local name=$1
    local dir=$2
    local cmd=$3
    
    echo "🔄 Starting $name..."
    cd "$dir"
    eval "$cmd" &
    local pid=$!
    echo $pid > "/tmp/${name}.pid"
    cd - > /dev/null
    echo "✅ $name started (PID: $pid)"
}

# Start mock restaurant servers
echo ""
echo "🍕 Starting Mock Restaurant Servers..."
start_service "Mock Restaurants" "apps/mock-restaurants" "make start-all"

# Wait a moment for servers to start
sleep 3

# Start A2A agents
echo ""
echo "🤖 Starting A2A Restaurant Agents..."
cd apps/restaurant-agents
make install > /dev/null 2>&1
start_service "A2A Agents" "apps/restaurant-agents" "make start-a2a-all"
cd - > /dev/null

# Wait a moment for A2A servers to start
sleep 3

# Start MCP client
echo ""
echo "🔌 Starting MCP Restaurant Client..."
cd apps/mcp-restaurant-client
make install > /dev/null 2>&1
start_service "MCP Client" "apps/mcp-restaurant-client" "make run"
cd - > /dev/null

# Wait a moment for MCP server to start
sleep 2

echo ""
echo "🎉 Restaurant A2A Demo is running!"
echo "=================================="
echo ""
echo "📋 Services:"
echo "  • Mock Restaurants: http://localhost:8001-8003"
echo "  • A2A Agents: http://localhost:4001-4003"
echo "  • MCP Client: http://localhost:3000"
echo ""
echo "🔗 Test endpoints:"
echo "  • OTTO Portland: http://localhost:8001/health"
echo "  • Street Exeter: http://localhost:8002/health"
echo "  • Newick's Lobster: http://localhost:8003/health"
echo "  • A2A Discovery: http://localhost:4001/.well-known/agents.json"
echo ""
echo "🛑 To stop all services, run: ./stop_restaurant_demo.sh"
echo ""
echo "📖 For more information, see: RESTAURANT_A2A_SETUP.md"
