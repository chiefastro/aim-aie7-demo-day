from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dice_roller import DiceRoller
from ascii_game import game

load_dotenv()

mcp = FastMCP("mcp-server")

@mcp.tool()
def start_game(player_name: str) -> str:
    """Start a new ASCII adventure game with the given player name"""
    return game.start_game(player_name)

@mcp.tool()
def game_look() -> str:
    """Look around the current room in the ASCII game"""
    return game.look()

@mcp.tool()
def game_move(direction: str) -> str:
    """Move in the specified direction (north, south, east, west) in the ASCII game"""
    return game.move(direction)

@mcp.tool()
def game_take(item_name: str) -> str:
    """Take an item from the current room in the ASCII game"""
    return game.take(item_name)

@mcp.tool()
def game_inventory() -> str:
    """Check your inventory in the ASCII game"""
    return game.inventory()

@mcp.tool()
def game_status() -> str:
    """Check your health and stats in the ASCII game"""
    return game.status()

@mcp.tool()
def game_attack() -> str:
    """Attack the current enemy in the ASCII game"""
    return game.attack()

@mcp.tool()
def game_use(item_name: str) -> str:
    """Use an item from your inventory in the ASCII game"""
    return game.use(item_name)

@mcp.tool()
def game_help() -> str:
    """Show help information for the ASCII game"""
    return game.help()

@mcp.tool()
def game_state() -> str:
    """Get the current game state summary"""
    return game.get_game_state()

if __name__ == "__main__":
    mcp.run(transport="stdio")