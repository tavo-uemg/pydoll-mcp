#!/usr/bin/env python3

import asyncio
import sys

# Add PyDoll to path
sys.path.insert(0, '/opt/pydoll_env/lib/python3.11/site-packages')

# Import our MCP server functions
exec(open('/usr/local/bin/pydoll-mcp').read())

async def test_start_browser():
    """Test the start_browser_session function directly"""
    print("Testing start_browser_session function...")
    
    try:
        # Create a browser session first
        result1 = await create_browser_session("test_direct", headless=True)
        print(f"Create result: {result1}")
        
        # Start the browser session
        result2 = await start_browser_session("test_direct")
        print(f"Start result: {result2}")
        
        # List sessions
        result3 = await list_sessions()
        print(f"Sessions: {result3}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_start_browser())