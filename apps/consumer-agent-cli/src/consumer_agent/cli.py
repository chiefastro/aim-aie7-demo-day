"""Consumer Agent CLI - Interactive interface for discovering and interacting with ACP offers"""

import asyncio
import click
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import Dict, Any, Optional

from .mcp_client import MCPClient
from .config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for beautiful output
console = Console()


class ConsumerAgentCLI:
    """Interactive CLI for consumer agent operations"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.session_data = {}
    
    async def start(self):
        """Start the interactive CLI session"""
        console.print(Panel.fit(
            "[bold blue]🍕 ACP Consumer Agent CLI[/bold blue]\n"
            "Discover and interact with restaurant offers using AI-powered search",
            title="Welcome to Agentic Commerce Protocol"
        ))
        
        # Check MCP connection
        if not await self.mcp_client.connect():
            console.print("[red]❌ Failed to connect to MCP server[/red]")
            return
        
        console.print("[green]✅ Connected to MCP server[/green]")
        
        # Main interaction loop
        await self.main_menu()
    
    async def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            console.print("\n[bold cyan]Main Menu:[/bold cyan]")
            console.print("1. 🔍 Search for offers")
            console.print("2. 📍 Find nearby offers")
            console.print("3. 📋 Get offer details")
            console.print("4. 🎯 Demo workflow")
            console.print("5. 📊 Show session info")
            console.print("6. 🚪 Exit")
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                await self.search_offers()
            elif choice == "2":
                await self.find_nearby_offers()
            elif choice == "3":
                await self.get_offer_details()
            elif choice == "4":
                await self.demo_workflow()
            elif choice == "5":
                await self.show_session_info()
            elif choice == "6":
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
    
    async def search_offers(self):
        """Search for offers using semantic query"""
        console.print("\n[bold green]🔍 Search for Offers[/bold green]")
        
        # Get search parameters
        query = Prompt.ask("Enter search query", default="pizza")
        
        # Optional geo parameters
        use_geo = Confirm.ask("Include location search?")
        lat, lng, radius = None, None, 50000
        
        if use_geo:
            try:
                lat = float(Prompt.ask("Latitude", default="42.3601"))
                lng = float(Prompt.ask("Longitude", default="-71.0589"))
                radius = int(Prompt.ask("Radius (meters)", default="50000"))
            except ValueError:
                console.print("[red]❌ Invalid coordinates[/red]")
                return
        
        # Optional labels
        use_labels = Confirm.ask("Filter by labels?")
        labels = []
        if use_labels:
            labels_input = Prompt.ask("Enter labels (comma-separated)", default="pizza,delivery")
            labels = [label.strip() for label in labels_input.split(",") if label.strip()]
        
        # Optional limit
        limit = int(Prompt.ask("Maximum results", default="10"))
        
        # Execute search
        console.print(f"\n[blue]Searching for '{query}'...[/blue]")
        
        try:
            result = await self.mcp_client.search_offers(
                query=query,
                lat=lat,
                lng=lng,
                radius_m=radius,
                labels=labels,
                limit=limit
            )
            
            if result:
                # Store results in session
                self.session_data["last_search"] = {
                    "query": query,
                    "results": result,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Display results
                await self.display_search_results(result)
            else:
                console.print("[yellow]⚠️  No results found[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ Search failed: {e}[/red]")
    
    async def find_nearby_offers(self):
        """Find offers near a specific location"""
        console.print("\n[bold green]📍 Find Nearby Offers[/bold green]")
        
        try:
            lat = float(Prompt.ask("Latitude", default="42.3601"))
            lng = float(Prompt.ask("Longitude", default="-71.0589"))
            radius = int(Prompt.ask("Radius (meters)", default="25000"))
            limit = int(Prompt.ask("Maximum results", default="10"))
        except ValueError:
            console.print("[red]❌ Invalid coordinates[/red]")
            return
        
        console.print(f"\n[blue]Finding offers within {radius}m of ({lat}, {lng})...[/blue]")
        
        try:
            result = await self.mcp_client.get_nearby_offers(
                lat=lat,
                lng=lng,
                radius_m=radius,
                limit=limit
            )
            
            if result:
                # Store results in session
                self.session_data["last_nearby"] = {
                    "lat": lat,
                    "lng": lng,
                    "radius": radius,
                    "results": result,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Display results
                await self.display_search_results(result)
            else:
                console.print("[yellow]⚠️  No nearby offers found[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ Nearby search failed: {e}[/red]")
    
    async def get_offer_details(self):
        """Get detailed information about a specific offer"""
        console.print("\n[bold green]📋 Get Offer Details[/bold green]")
        
        offer_id = Prompt.ask("Enter offer ID")
        if not offer_id:
            console.print("[red]❌ Offer ID is required[/red]")
            return
        
        console.print(f"\n[blue]Fetching details for offer {offer_id}...[/blue]")
        
        try:
            offer = await self.mcp_client.get_offer_by_id(offer_id)
            
            if offer:
                # Store in session
                self.session_data["last_offer"] = {
                    "offer_id": offer_id,
                    "offer": offer,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Display offer details
                await self.display_offer_details(offer)
            else:
                console.print("[yellow]⚠️  Offer not found[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ Failed to get offer: {e}[/red]")
    
    async def demo_workflow(self):
        """Run a complete demo workflow"""
        console.print("\n[bold green]🎯 Demo Workflow[/bold green]")
        console.print("This will demonstrate a complete ACP workflow:")
        console.print("1. Search for pizza offers")
        console.print("2. Get details for a specific offer")
        console.print("3. Show how an agent would use this information")
        
        if not Confirm.ask("Continue with demo?"):
            return
        
        try:
            # Step 1: Search for pizza offers
            console.print("\n[blue]Step 1: Searching for pizza offers...[/blue]")
            search_result = await self.mcp_client.search_offers(
                query="pizza",
                lat=42.3601,
                lng=-71.0589,
                radius_m=50000,
                labels=["pizza"],
                limit=5
            )
            
            if not search_result:
                console.print("[yellow]⚠️  No pizza offers found for demo[/yellow]")
                return
            
            # Step 2: Get details for first offer
            first_offer = search_result.get("offers", [{}])[0]
            offer_id = first_offer.get("offer_id")
            
            if offer_id:
                console.print(f"\n[blue]Step 2: Getting details for offer {offer_id}...[/blue]")
                offer_details = await self.mcp_client.get_offer_by_id(offer_id)
                
                if offer_details:
                    # Step 3: Show agent decision process
                    console.print("\n[blue]Step 3: Agent decision process...[/blue]")
                    await self.show_agent_decision(search_result, offer_details)
                else:
                    console.print("[yellow]⚠️  Could not get offer details[/yellow]")
            
            console.print("\n[green]✅ Demo workflow completed![/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Demo workflow failed: {e}[/red]")
    
    async def show_agent_decision(self, search_results, selected_offer):
        """Show how an AI agent would make decisions based on the data"""
        console.print("\n[bold cyan]🤖 AI Agent Decision Process[/bold cyan]")
        
        # Analyze search results
        total_offers = len(search_results.get("offers", []))
        console.print(f"📊 Found {total_offers} offers to evaluate")
        
        # Show selection criteria
        console.print("\n[bold]Selection Criteria:[/bold]")
        console.print("• Relevance to user query")
        console.print("• Geographic proximity")
        console.print("• Bounty amount")
        console.print("• Merchant reputation")
        console.print("• Offer validity")
        
        # Show selected offer reasoning
        if selected_offer:
            console.print(f"\n[bold]Selected Offer: {selected_offer.get('offer_id')}[/bold]")
            
            # Extract key decision factors
            merchant_name = selected_offer.get("merchant", {}).get("name", "Unknown")
            bounty_amount = selected_offer.get("bounty", {}).get("amount", 0)
            labels = selected_offer.get("labels", [])
            
            console.print(f"🏪 Merchant: {merchant_name}")
            console.print(f"💰 Bounty: ${bounty_amount}")
            console.print(f"🏷️  Labels: {', '.join(labels)}")
            
            # Show next steps
            console.print("\n[bold]Next Steps:[/bold]")
            console.print("1. Present offer to user")
            console.print("2. Initiate checkout process")
            console.print("3. Handle order confirmation")
            console.print("4. Process attribution receipt")
    
    async def display_search_results(self, results):
        """Display search results in a formatted table"""
        offers = results.get("offers", [])
        total = results.get("total", 0)
        
        console.print(f"\n[green]✅ Found {total} offers[/green]")
        
        if not offers:
            return
        
        # Create results table
        table = Table(title="Search Results")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Offer ID", style="magenta")
        table.add_column("Title", style="green")
        table.add_column("Merchant", style="blue")
        table.add_column("Bounty", style="yellow")
        table.add_column("Labels", style="white")
        
        for i, offer in enumerate(offers, 1):
            table.add_row(
                str(i),
                offer.get("offer_id", "N/A"),
                offer.get("title", "N/A"),
                offer.get("merchant", {}).get("name", "N/A"),
                f"${offer.get('bounty', {}).get('amount', 0)}" if offer.get("bounty") else "N/A",
                ", ".join(offer.get("labels", []))
            )
        
        console.print(table)
        
        # Store results for later use
        self.session_data["current_results"] = results
    
    async def display_offer_details(self, offer):
        """Display detailed offer information"""
        console.print(f"\n[bold green]📋 Offer Details: {offer.get('offer_id')}[/bold green]")
        
        # Create details panel
        details = []
        
        if offer.get("title"):
            details.append(f"[bold]Title:[/bold] {offer['title']}")
        
        if offer.get("description"):
            details.append(f"[bold]Description:[/bold] {offer['description']}")
        
        if offer.get("merchant"):
            merchant = offer["merchant"]
            details.append(f"[bold]Merchant:[/bold] {merchant.get('name', 'N/A')}")
            
            if merchant.get("location"):
                loc = merchant["location"]
                address_parts = []
                if loc.get("address"):
                    address_parts.append(loc["address"])
                if loc.get("city"):
                    address_parts.append(loc["city"])
                if loc.get("state"):
                    address_parts.append(loc["state"])
                
                if address_parts:
                    details.append(f"[bold]Location:[/bold] {', '.join(address_parts)}")
        
        if offer.get("bounty"):
            bounty = offer["bounty"]
            details.append(f"[bold]Bounty:[/bold] ${bounty.get('amount', 0)} {bounty.get('currency', 'USD')}")
            
            if bounty.get("revenue_split"):
                splits = []
                for party, share in bounty["revenue_split"].items():
                    splits.append(f"{party}: {share}%")
                details.append(f"[bold]Revenue Split:[/bold] {', '.join(splits)}")
        
        if offer.get("labels"):
            details.append(f"[bold]Labels:[/bold] {', '.join(offer['labels'])}")
        
        if offer.get("terms"):
            terms = offer["terms"]
            if terms.get("valid_days"):
                details.append(f"[bold]Valid Days:[/bold] {', '.join(terms['valid_days'])}")
        
        # Display details
        for detail in details:
            console.print(detail)
    
    async def show_session_info(self):
        """Display current session information"""
        console.print("\n[bold cyan]📊 Session Information[/bold cyan]")
        
        if not self.session_data:
            console.print("[yellow]No session data available[/yellow]")
            return
        
        # Show last search
        if "last_search" in self.session_data:
            search = self.session_data["last_search"]
            console.print(f"\n[bold]Last Search:[/bold]")
            console.print(f"  Query: {search['query']}")
            console.print(f"  Results: {search['results'].get('total', 0)} offers")
            console.print(f"  Timestamp: {search['timestamp']:.2f}s ago")
        
        # Show last nearby search
        if "last_nearby" in self.session_data:
            nearby = self.session_data["last_nearby"]
            console.print(f"\n[bold]Last Nearby Search:[/bold]")
            console.print(f"  Location: ({nearby['lat']}, {nearby['lng']})")
            console.print(f"  Radius: {nearby['radius']}m")
            console.print(f"  Results: {nearby['results'].get('total', 0)} offers")
        
        # Show last offer details
        if "last_offer" in self.session_data:
            offer = self.session_data["last_offer"]
            console.print(f"\n[bold]Last Offer Details:[/bold]")
            console.print(f"  Offer ID: {offer['offer_id']}")
            console.print(f"  Timestamp: {offer['timestamp']:.2f}s ago")


@click.command()
@click.option("--host", default="localhost", help="MCP server host")
@click.option("--port", default=3002, help="MCP server port")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(host: str, port: int, debug: bool):
    """ACP Consumer Agent CLI - Interactive interface for discovering offers"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update config
    config.MCP_HOST = host
    config.MCP_PORT = port
    
    # Create and run CLI
    cli = ConsumerAgentCLI()
    
    try:
        asyncio.run(cli.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        if debug:
            raise


if __name__ == "__main__":
    main()
