#!/bin/bash

# Restaurant A2A Demo Stop Script
# This script stops all components of the restaurant A2A demo

echo "🛑 Stopping Restaurant A2A Demo..."
echo "=================================="

# Function to stop service by PID file
stop_service() {
    local name=$1
    local pid_file="/tmp/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "🔄 Stopping $name (PID: $pid)..."
            kill $pid
            wait $pid 2>/dev/null || true
            echo "✅ $name stopped"
        else
            echo "⚠️  $name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  No PID file found for $name"
    fi
}

# Stop services
echo ""
echo "🔄 Stopping services..."

# Stop MCP client
stop_service "MCP Client"

# Stop A2A agents
stop_service "A2A Agents"

# Stop mock restaurants
stop_service "Mock Restaurants"

# Kill any remaining processes
echo ""
echo "🧹 Cleaning up remaining processes..."

# Kill restaurant agent processes
pkill -f "restaurant_agents" 2>/dev/null || true
pkill -f "mcp_restaurant_client" 2>/dev/null || true
pkill -f "mock-restaurants" 2>/dev/null || true

# Kill processes on specific ports
for port in 8001 8002 8003 4001 4002 4003 3000; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "🔄 Stopping process on port $port..."
        lsof -Pi :$port -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
    fi
done

echo ""
echo "✅ Restaurant A2A Demo stopped!"
echo "=================================="
