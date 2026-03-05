import asyncio
from pydantic_ai.mcp import MCPServerStdio
from pathlib import Path
import os

async def main():
    # Get the absolute path to the qna server directory
    qna_path = "../qna"
    working_dir = os.getcwd()
    print(f"Current file: {working_dir}")
    print(f"QNA path: {qna_path}")
    print(f"DB path: {'data/chinook.db'}")
    
    # Create MCPServerStdio instance
    mcp_server = MCPServerStdio(
        command="uv",
        args=[
            "--directory",
            qna_path,
            "run",
            "mcp-server-qna",
            "--db-path",
            "data/chinook.db"
        ],
    )

    # Use as async context manager to start the server
    async with mcp_server:
        print("\n→ MCP Server started successfully!")
        
        # List available tools
        print("\n→ Listing available tools...")
        tools = await mcp_server.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Test lookup_track tool using direct_call_tool
        print("\n=== Testing lookup_track ===")
        result = await mcp_server.call_tool("lookup_track", {"artist_name": "AC/DC"})
        print(f"Result: {result}")
        
        # Test lookup_album tool
        print("\n=== Testing lookup_album ===")
        result = await mcp_server.call_tool("lookup_album", {"artist_name": "AC/DC"})
        print(f"Result: {result}")
        
        # Test lookup_artist tool
        print("\n=== Testing lookup_artist ===")
        result = await mcp_server.call_tool("lookup_artist", {"artist_name": "AC/DC"})
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())