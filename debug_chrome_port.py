#!/usr/bin/env python3

import asyncio
import sys
import subprocess
import time

# Add PyDoll to path
sys.path.insert(0, '/opt/pydoll_env/lib/python3.11/site-packages')

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def debug_chrome_process():
    """Debug Chrome process and port allocation"""
    print("=== Chrome Process Debug ===")
    
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
        
        # Check what port PyDoll assigned
        print(f"PyDoll assigned port: {browser._connection_port}")
        
        # Check Chrome processes before starting
        print("\n=== Chrome processes BEFORE browser.start() ===")
        result = subprocess.run(["pgrep", "-f", "chrome.*remote-debugging"], capture_output=True, text=True)
        print(f"Chrome processes: {result.stdout.strip() if result.stdout.strip() else 'None'}")
        
        print("\nStarting browser...")
        initial_tab = await browser.start()
        
        print(f"Browser started successfully!")
        print(f"Initial tab: {initial_tab}")
        
        # Check Chrome processes after starting
        print("\n=== Chrome processes AFTER browser.start() ===")
        result = subprocess.run(["pgrep", "-f", "chrome.*remote-debugging"], capture_output=True, text=True)
        if result.stdout.strip():
            for pid in result.stdout.strip().split('\n'):
                cmd_result = subprocess.run(["ps", "-p", pid, "-o", "command="], capture_output=True, text=True)
                print(f"PID {pid}: {cmd_result.stdout.strip()}")
        else:
            print("No Chrome processes with remote-debugging found")
        
        # Check if we can connect to the debugging port
        print(f"\n=== Testing connection to port {browser._connection_port} ===")
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'http://localhost:{browser._connection_port}/json/version') as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Successfully connected to Chrome DevTools on port {browser._connection_port}")
                        print(f"Chrome version: {data.get('Browser', 'Unknown')}")
                        print(f"WebSocket URL: {data.get('webSocketDebuggerUrl', 'Not found')}")
                    else:
                        print(f"❌ HTTP {response.status} when connecting to port {browser._connection_port}")
            except Exception as e:
                print(f"❌ Failed to connect to port {browser._connection_port}: {e}")
        
        print("\nCreating new tab...")
        tab = await browser.new_tab()
        print(f"✅ New tab created: {tab}")
        
        print(f"\nNavigating to example.com...")
        await tab.go_to("https://example.com")
        current_url = await tab.current_url
        print(f"✅ Navigation completed! Current URL: {current_url}")
        
        print("\nCleaning up...")
        await tab.close()
        await browser.stop()
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chrome_process())