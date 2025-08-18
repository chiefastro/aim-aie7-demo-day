#!/usr/bin/env python3
"""Test script for Docker setup verification"""

import asyncio
import aiohttp
import time
import subprocess
import sys
from typing import Dict, List, Optional


class DockerSetupTester:
    """Test the Docker setup for ACP Demo"""
    
    def __init__(self):
        self.services = {
            "qdrant": {"url": "http://localhost:6333/health", "port": 6333},
            "gor-api": {"url": "http://localhost:3001/health", "port": 3001},
            "offer-scraper": {"url": "http://localhost:3000/demo", "port": 3000}
        }
        self.results = {}
    
    async def check_service_health(self, service_name: str, url: str) -> bool:
        """Check if a service is healthy"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"❌ {service_name}: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ {service_name}: {e}")
            return False
    
    async def test_all_services(self) -> Dict[str, bool]:
        """Test all services"""
        print("🏥 Testing service health...")
        
        for service_name, config in self.services.items():
            print(f"  Testing {service_name}...", end=" ")
            healthy = await self.check_service_health(service_name, config["url"])
            self.results[service_name] = healthy
            
            if healthy:
                print("✅")
            else:
                print("❌")
        
        return self.results
    
    def check_docker_status(self) -> Dict[str, str]:
        """Check Docker container status"""
        print("\n🐳 Checking Docker container status...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            status = {}
            
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        service = parts[0]
                        state = parts[1]
                        status[service] = state
                        print(f"  {service}: {state}")
            
            return status
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check Docker status: {e}")
            return {}
    
    def check_ports(self) -> Dict[str, bool]:
        """Check if ports are accessible"""
        print("\n🔌 Checking port accessibility...")
        
        import socket
        
        port_status = {}
        
        for service_name, config in self.services.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            try:
                result = sock.connect_ex(('localhost', config["port"]))
                sock.close()
                
                accessible = result == 0
                port_status[service_name] = accessible
                
                if accessible:
                    print(f"  Port {config['port']} ({service_name}): ✅")
                else:
                    print(f"  Port {config['port']} ({service_name}): ❌")
                    
            except Exception as e:
                print(f"  Port {config['port']} ({service_name}): ❌ ({e})")
                port_status[service_name] = False
        
        return port_status
    
    async def test_mcp_functionality(self) -> bool:
        """Test MCP server functionality"""
        print("\n🔧 Testing MCP server functionality...")
        
        try:
            # Test basic connectivity
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Test GOR API
                async with session.get("http://localhost:3001/offers?query=pizza&limit=1") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"  GOR API search: ✅ (found {data.get('results', {}).get('total', 0)} offers)")
                    else:
                        print(f"  GOR API search: ❌ (HTTP {response.status})")
                        return False
                
                # Test MCP server (if it has a health endpoint)
                try:
                    async with session.get("http://localhost:3002/health") as response:
                        if response.status == 200:
                            print("  MCP server health: ✅")
                        else:
                            print(f"  MCP server health: ❌ (HTTP {response.status})")
                except:
                    print("  MCP server health: ⚠️  (no health endpoint)")
                
                return True
                
        except Exception as e:
            print(f"  MCP functionality test: ❌ ({e})")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 DOCKER SETUP TEST SUMMARY")
        print("="*50)
        
        # Service health
        healthy_services = sum(1 for healthy in self.results.values() if healthy)
        total_services = len(self.results)
        
        print(f"🏥 Service Health: {healthy_services}/{total_services} healthy")
        for service, healthy in self.results.items():
            status = "✅" if healthy else "❌"
            print(f"  {status} {service}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if healthy_services == total_services:
            print("  🎉 All services are healthy! You can now run the demo.")
            print("  🚀 Try: make cli")
        elif healthy_services > 0:
            print("  ⚠️  Some services are not healthy. Check logs with: make logs")
            print("  🔄 Try restarting: make down && make up")
        else:
            print("  ❌ No services are healthy. Check if Docker is running.")
            print("  🚀 Try starting fresh: make start")
        
        print(f"\n📚 Useful commands:")
        print(f"  make help     - Show all available commands")
        print(f"  make status   - Check service status")
        print(f"  make logs     - View service logs")
        print(f"  make clean    - Clean up everything")
        print(f"  make reset    - Reset and start fresh")


async def main():
    """Main test function"""
    print("🚀 ACP Demo - Docker Setup Test")
    print("="*40)
    
    tester = DockerSetupTester()
    
    # Check Docker status
    docker_status = tester.check_docker_status()
    
    # Check ports
    port_status = tester.check_ports()
    
    # Test service health
    service_health = await tester.test_all_services()
    
    # Test MCP functionality
    mcp_working = await tester.test_mcp_functionality()
    
    # Print summary
    tester.print_summary()
    
    # Exit with appropriate code
    healthy_services = sum(1 for healthy in service_health.values() if healthy)
    total_services = len(service_health)
    
    if healthy_services == total_services:
        print("\n🎉 All tests passed! Docker setup is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_services - healthy_services} service(s) have issues.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
