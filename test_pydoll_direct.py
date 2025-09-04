#!/usr/bin/env python3

import asyncio
import sys
import os

# Add PyDoll to path
sys.path.insert(0, '/opt/pydoll_env/lib/python3.11/site-packages')

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def test_pydoll_direct():
    """Test PyDoll directly outside MCP context"""
    print("Testing PyDoll direct functionality...")
    
    try:
        # Create options
        options = ChromiumOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.binary_location = "/usr/bin/google-chrome"
        
        print("Creating Chrome browser...")
        browser = Chrome(options=options)
        
        print("Browser created successfully!")
        
        print("Starting Chrome process...")
        initial_tab = await browser.start()
        print(f"Chrome started with initial tab: {initial_tab}")
        
        print("Creating new tab...")
        tab = await browser.new_tab()
        print(f"Tab created: {tab}")
        
        print("Navigating to example.com...")
        await tab.go_to("https://example.com")
        print("Navigation completed!")
        
        print("Getting page URL...")
        url = await tab.current_url
        print(f"Current URL: {url}")
        
        print("Closing tab...")
        await tab.close()
        
        print("Stopping browser...")
        await browser.stop()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pydoll_direct())