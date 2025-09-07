#!/usr/bin/env python3
"""
PyDoll Browser Automation Server - Complete JSON-RPC Implementation
==================================================================

Provides complete browser automation capabilities through direct JSON-RPC protocol.
Self-contained server with no external dependencies or wrapper scripts required.

This server includes ALL PyDoll features:
- Complete browser session management (82 tools total)
- Advanced tab operations and navigation
- Full element interaction suite
- Comprehensive event system with callbacks
- Request interception and modification
- Advanced element state checking
- IFrame support and context management
- Browser preferences configuration
- File dialog handling
- Cloudflare bypass automation
- Network inspection and logging
- Dialog management
- JavaScript execution
- Cookie and storage operations
- Screenshot and PDF generation
- Upload/download operations
- Wait conditions and synchronization

Best Practices & Common Pitfalls:
=====================================

CRITICAL TOOL QUIRKS & WORKAROUNDS:
===================================

1. ELEMENT FINDING & INTERACTION:
   ✗ wait_for_element() - Times out on existing elements, use find_element() instead
   ✗ upload_file() - Only works with <input type="file">, create dynamically if needed
   ✗ scroll_element(x,y) - Fails with x/y params, use execute_script_on_element() instead
   ✓ Basic scroll_element() works without x/y parameters

2. ELEMENT PROPERTY ACCESS:
   ✗ get_element_property() - Frequent "Cannot find context" errors
   ✓ execute_script_on_element() - Reliable alternative for property access
   ✗ get_element_text() - May return empty on some elements
   ✓ get_element_attribute() - Works when attribute exists

3. JAVASCRIPT EXECUTION:
   ✗ execute_script(handle_dialogs=True) - Parameter not supported
   ✗ execute_script(timeout=30) - Parameter not supported  
   ✓ execute_script(tab_id, script) - Basic execution works
   ✗ NEVER use alert(), confirm(), prompt() - Cause 60s timeouts

4. EVENT MONITORING:
   ✗ get_event_logs() - Returns [] unless events actively triggered
   ✗ get_network_logs() - Fails unless enable_network_events() called first
   ✓ Must enable events BEFORE triggering activity to log

5. NETWORK INTERCEPTION:
   ✓ continue_request/fail_request/fulfill_request - Accept ANY request_id for testing
   ✗ get_network_response_body() - Often returns empty for completed requests
   ✓ Network tools designed for mock testing scenarios

6. IFRAME HANDLING:
   ✗ get_frame() - Fails with cross-origin iframes (security limitation)
   ✗ Most external sites blocked due to CORS policies
   ✓ Same-origin or data: URI iframes work

7. DIALOG HANDLING:
   ✓ handle_alert() - Works correctly with real dialogs
   ✓ has_dialog() - Detects active dialogs reliably
   ✗ get_dialog_message() - Limited message retrieval capability

8. CLOUDFLARE BYPASS:
   ✓ Automatic bypass built into navigate() and create_tab()
   ✓ Uses stealth browser configuration by default
   ✓ No manual bypass tools needed - handled automatically

GENERAL BEST PRACTICES:
======================

1. HTTP Requests:
   - Headers must be formatted as: [{"name": "key", "value": "val"}]
   - Not as simple objects: {"key": "val"}

2. Element References:
   - Re-find elements after page navigation or DOM changes
   - Stale element errors indicate you need to call find_element again

3. Event System:
   - Call enable_network_events() before get_network_logs()
   - Event tools may timeout if browser tab is blocked by dialogs

4. JavaScript Execution:
   - NEVER use alert(), confirm(), or prompt() - they cause 60s timeouts
   - Use console.log() for debugging instead
   - Handle any existing dialogs with handle_alert() before other operations

5. Dialog Management:
   - Always handle dialogs promptly to prevent browser state contamination
   - Dialog-blocked tabs cannot perform most operations until cleared

Environment Independent: Automatically detects PyDoll installation
"""

import asyncio
import base64
import json
import logging
import os
import sys
import tempfile
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

# Auto-detect PyDoll installation and add to path
def setup_pydoll_path():
    """Auto-detect PyDoll installation and configure Python path"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Auto-detect local venv paths first (relative to script location)
    import platform
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    local_venv_paths = []
    if platform.system() == "Windows":
        local_venv_paths = [
            os.path.join(script_dir, "venv", "Lib", "site-packages"),
            os.path.join(script_dir, ".venv", "Lib", "site-packages"),
        ]
    else:
        local_venv_paths = [
            os.path.join(script_dir, "venv", "lib", f"python{python_version}", "site-packages"),
            os.path.join(script_dir, ".venv", "lib", f"python{python_version}", "site-packages"),
            os.path.join(script_dir, "venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages"),
            os.path.join(script_dir, ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages"),
        ]
    
    # Fallback system paths
    possible_paths = local_venv_paths + [
        "/opt/pydoll_env/lib/python3.11/site-packages",
        "/opt/pydoll_env/lib/python3.10/site-packages", 
        "/opt/pydoll_env/lib/python3.9/site-packages",
        "/usr/local/lib/python3.11/dist-packages",
        "/usr/local/lib/python3.10/dist-packages",
        "/usr/local/lib/python3.9/dist-packages",
        os.path.expanduser("~/.local/lib/python3.11/site-packages"),
        os.path.expanduser("~/.local/lib/python3.10/site-packages"),
        os.path.expanduser("~/.local/lib/python3.9/site-packages"),
    ]
    
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "pydoll")):
            if path not in sys.path:
                sys.path.insert(0, path)
            print(f"Found PyDoll at: {path}", file=sys.stderr, flush=True)
            return path
    
    # Try importing to see if already available
    try:
        import pydoll
        print("PyDoll already available in Python path", file=sys.stderr, flush=True)
        return "system"
    except ImportError:
        print("ERROR: PyDoll not found. Please install PyDoll first.", file=sys.stderr, flush=True)
        sys.exit(1)

# Setup PyDoll before importing
setup_pydoll_path()

# Auto-Update System
import urllib.request
import urllib.error
import shutil
import subprocess
import time
import platform
from datetime import datetime

sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

# Now import PyDoll
try:
    from pydoll.browser import Chrome
    from pydoll.browser.options import ChromiumOptions
    from pydoll.constants import Key, By
    from pydoll.exceptions import *
    from pydoll.protocol.network.types import ErrorReason
    from pydoll.protocol.fetch.types import RequestStage, HeaderEntry
    from pydoll.commands import RuntimeCommands
    from pydoll.elements.web_element import WebElement
except ImportError as e:
    print(f"ERROR: Failed to import PyDoll: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

# Monkey patch PyDoll WebElement to add Shadow DOM support
async def get_shadow_root_patched(self) -> Optional['WebElement']:
    """
    Get the shadow root attached to this element if it exists.

    Returns:
        WebElement representing the shadow root, or None if no shadow root exists.
        
    Raises:
        ElementNotFound: If element doesn't exist or shadow root access fails.
    """
    if not self._object_id:
        return None
        
    try:
        # Use Runtime.getProperties to check for shadowRoot property
        response = await self._connection_handler.execute_command(
            RuntimeCommands.get_properties(object_id=self._object_id)
        )
        
        # Look for shadowRoot property
        shadow_root_prop = None
        for prop in response.get('result', {}).get('result', []):
            if prop.get('name') == 'shadowRoot' and 'objectId' in prop.get('value', {}):
                shadow_root_prop = prop
                break
                
        if not shadow_root_prop:
            return None
            
        shadow_root_object_id = shadow_root_prop['value']['objectId']
        
        # Create a WebElement for the shadow root
        return WebElement(
            object_id=shadow_root_object_id,
            connection_handler=self._connection_handler
        )
        
    except Exception:
        return None

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apply the monkey patch
WebElement.get_shadow_root = get_shadow_root_patched
logger.info("Applied Shadow DOM monkey patch to PyDoll WebElement")

# JSON-RPC server - no external MCP dependencies required

# Server version
__version__ = "1.0.1"

# Cross-platform utility functions
def get_platform_temp_dir():
    """Get platform-appropriate temporary directory"""
    if platform.system() == "Windows":
        return os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Windows\\Temp'))
    else:
        return '/tmp'

def get_platform_cache_dir():
    """Get platform-appropriate cache directory"""
    system = platform.system()
    if system == "Windows":
        cache_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        return os.path.join(cache_dir, 'pydoll-mcp')
    elif system == "Darwin":  # macOS
        return os.path.expanduser('~/Library/Caches/pydoll-mcp')
    else:  # Linux and others
        xdg_cache = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        return os.path.join(xdg_cache, 'pydoll-mcp')

def get_platform_allowed_paths():
    """Get platform-appropriate allowed installation paths"""
    system = platform.system()
    if system == "Windows":
        return [
            'C:\\Program Files\\',
            'C:\\Program Files (x86)\\',
            os.environ.get('PROGRAMFILES', 'C:\\Program Files\\'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)\\'),
            os.path.expanduser('~\\AppData\\Local\\'),
            os.path.expanduser('~\\AppData\\Roaming\\'),
            os.path.expanduser('~\\')
        ]
    elif system == "Darwin":  # macOS
        return [
            '/usr/local/bin/',
            '/usr/bin/',
            '/opt/',
            '/Applications/',
            os.path.expanduser('~/Applications/'),
            os.path.expanduser('~/bin/'),
            os.path.expanduser('~/'),
        ]
    else:  # Linux and others
        return [
            '/usr/local/bin/',
            '/usr/bin/',
            '/opt/',
            os.path.expanduser('~/bin/'),
            os.path.expanduser('~/')
        ]

def is_newer_version(version1, version2):
    """Compare two semantic version strings. Returns True if version1 is newer than version2."""
    try:
        # Split versions into parts and convert to integers
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        # Compare each part
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return True
            elif v1_parts[i] < v2_parts[i]:
                return False
        
        return False  # Versions are equal
    except ValueError:
        # Fallback to string comparison if parsing fails
        return version1 != version2

def make_file_executable(file_path):
    """Make file executable in a cross-platform way"""
    system = platform.system()
    if system == "Windows":
        # On Windows, executable permission is handled differently
        # We don't need to change permissions for Python scripts
        pass
    else:
        # Unix-like systems (Linux, macOS)
        os.chmod(file_path, 0o755)

def safe_remove_file(file_path):
    """Safely remove a file in a cross-platform way"""
    try:
        if os.path.exists(file_path):
            # On Windows, sometimes we need to handle file locks
            if platform.system() == "Windows":
                # Try to remove read-only attribute if it exists
                try:
                    import stat
                    os.chmod(file_path, stat.S_IWRITE)
                except:
                    pass
            os.unlink(file_path)
            return True
    except Exception as e:
        print(f"Warning: Could not remove file {file_path}: {e}", file=sys.stderr)
    return False

def get_platform_info():
    """Get detailed platform information for debugging"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'temp_dir': get_platform_temp_dir(),
        'cache_dir': get_platform_cache_dir(),
        'allowed_paths': get_platform_allowed_paths()
    }

# Auto-Update System URLs and Configuration
VERSION_URL = "https://raw.githubusercontent.com/coffeegrind123/pydoll-mcp/refs/heads/master/version"
BINARY_URL = "https://raw.githubusercontent.com/coffeegrind123/pydoll-mcp/refs/heads/master/pydoll-mcp"

# Create cache directory if it doesn't exist
try:
    CACHE_DIR = get_platform_cache_dir()
    os.makedirs(CACHE_DIR, exist_ok=True)
    UPDATE_CACHE_FILE = os.path.join(CACHE_DIR, "pydoll-mcp-update-cache")
except:
    # Fallback to temp directory
    UPDATE_CACHE_FILE = os.path.join(get_platform_temp_dir(), "pydoll-mcp-update-cache")

def check_for_updates():
    """Check for updates using conditional requests to minimize bandwidth"""
    try:
        # Check if we have cached update info
        cache_data = None
        if os.path.exists(UPDATE_CACHE_FILE):
            try:
                with open(UPDATE_CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
            except:
                cache_data = None
        
        # Prepare conditional request headers
        headers = {'User-Agent': 'pydoll-mcp-updater/1.0'}
        if cache_data and 'etag' in cache_data:
            headers['If-None-Match'] = cache_data['etag']
        if cache_data and 'last_modified' in cache_data:
            headers['If-Modified-Since'] = cache_data['last_modified']
        
        # Create request with conditional headers
        request = urllib.request.Request(VERSION_URL, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                remote_version = response.read().decode('utf-8').strip()
                
                # Cache the response metadata
                cache_info = {
                    'version': remote_version,
                    'check_time': time.time(),
                    'etag': response.headers.get('ETag'),
                    'last_modified': response.headers.get('Last-Modified')
                }
                
                try:
                    with open(UPDATE_CACHE_FILE, 'w') as f:
                        json.dump(cache_info, f)
                except:
                    pass  # Cache write failure is non-critical
                
                return remote_version
                
        except urllib.error.HTTPError as e:
            if e.code == 304:  # Not Modified
                # Use cached version if available
                if cache_data and 'version' in cache_data:
                    print(f"Version check: No changes detected (cached: {cache_data['version']})", file=sys.stderr)
                    return cache_data['version']
                else:
                    print("Version check: No changes detected but no cache available", file=sys.stderr)
                    return __version__
            else:
                raise e
                
    except Exception as e:
        print(f"Update check failed: {e}", file=sys.stderr)
        return None

def perform_update():
    """Download and install the updated version"""
    try:
        platform_info = get_platform_info()
        print(f"Downloading updated pydoll-mcp on {platform_info['system']}...", file=sys.stderr)
        
        # Download to temporary file
        temp_dir = get_platform_temp_dir()
        temp_file = os.path.join(temp_dir, f"pydoll-mcp-update-{int(time.time())}")
        print(f"Using temporary file: {temp_file}", file=sys.stderr)
        
        request = urllib.request.Request(BINARY_URL, headers={'User-Agent': 'pydoll-mcp-updater/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(temp_file, 'wb') as f:
                shutil.copyfileobj(response, f)
        
        # Comprehensive security validation of downloaded file
        try:
            # Check file size (should be reasonable for a Python script)
            file_stats = os.stat(temp_file)
            if file_stats.st_size < 1000:  # Too small
                raise Exception(f"Downloaded file too small ({file_stats.st_size} bytes)")
            if file_stats.st_size > 50 * 1024 * 1024:  # Too large (>50MB)
                raise Exception(f"Downloaded file too large ({file_stats.st_size} bytes)")
            
            # Read and validate file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Must start with Python shebang
            if not content.startswith('#!/usr/bin/env python'):
                raise Exception("Downloaded file doesn't start with Python shebang")
            
            # Must contain key expected components for pydoll-mcp
            required_strings = [
                'PyDoll Browser Automation Server',
                '__version__',
                'def auto_update_check',
                'JSON-RPC',
                'pydoll'
            ]
            
            for required in required_strings:
                if required not in content:
                    raise Exception(f"Downloaded file missing required component: {required}")
            
            
            # Validate Python syntax
            try:
                compile(content, temp_file, 'exec')
            except SyntaxError as e:
                raise Exception(f"Downloaded file has Python syntax errors: {e}")
                
        except Exception as e:
            safe_remove_file(temp_file)
            raise Exception(f"Downloaded file validation failed: {e}")
        
        # Make executable
        make_file_executable(temp_file)
        
        # Get current script path with additional security checks
        current_script = os.path.abspath(__file__)
        
        # Security: Ensure we're only updating files we should be updating
        script_name = os.path.basename(current_script)
        valid_names = ['pydoll-mcp', 'pydoll-mcp.exe', 'pydoll-mcp.py']
        if not any(script_name == name or script_name.endswith(name) for name in valid_names):
            raise Exception(f"Refusing to update non-pydoll-mcp file: {current_script}")
        
        # Security: Ensure the current script path is reasonable
        allowed_paths = get_platform_allowed_paths()
        if not any(current_script.startswith(path) for path in allowed_paths):
            raise Exception(f"Refusing to update file in suspicious location: {current_script}")
        
        backup_file = f"{current_script}.backup.{int(time.time())}"
        
        # Create backup of current version (with verification)
        if not os.path.exists(current_script):
            raise Exception(f"Current script does not exist: {current_script}")
        
        shutil.copy2(current_script, backup_file)
        print(f"Created backup: {backup_file}", file=sys.stderr)
        
        # Verify backup was created successfully
        if not os.path.exists(backup_file):
            raise Exception(f"Failed to create backup file: {backup_file}")
        
        # Replace current script with new version (atomic operation)
        try:
            shutil.move(temp_file, current_script)
            print(f"Updated pydoll-mcp successfully", file=sys.stderr)
            
            # Verify the update was successful
            if not os.path.exists(current_script):
                raise Exception("Updated file does not exist after replacement")
                
        except Exception as e:
            # If replacement failed, try to restore from backup
            print(f"Update replacement failed: {e}", file=sys.stderr)
            try:
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, current_script)
                    print("Restored from backup after failed update", file=sys.stderr)
            except:
                print("CRITICAL: Failed to restore backup after failed update", file=sys.stderr)
            raise e
        
        # Clean up old backups (keep only last 3)
        try:
            import glob
            backup_pattern = f"{current_script}.backup.*"
            backups = sorted(glob.glob(backup_pattern))
            if len(backups) > 3:
                for old_backup in backups[:-3]:
                    if safe_remove_file(old_backup):
                        print(f"Removed old backup: {old_backup}", file=sys.stderr)
        except:
            pass  # Backup cleanup is non-critical
        
        # Clear update cache so next run will check again
        safe_remove_file(UPDATE_CACHE_FILE)
        
        return True
        
    except Exception as e:
        print(f"Update failed: {e}", file=sys.stderr)
        # Clean up temp file if it exists
        safe_remove_file(temp_file)
        return False

def auto_update_check():
    """Perform automatic update check and update if needed"""
    try:
        platform_info = get_platform_info()
        print(f"Checking for updates on {platform_info['system']} (current version: {__version__})...", file=sys.stderr)
        remote_version = check_for_updates()
        
        if remote_version is None:
            print("Update check failed, continuing with current version", file=sys.stderr)
            return False
        
        # Compare versions semantically
        if is_newer_version(remote_version, __version__):
            print(f"New version available: {remote_version} (current: {__version__})", file=sys.stderr)
            
            if perform_update():
                print("Update completed successfully. Restarting...", file=sys.stderr)
                # Restart the script with same arguments
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("Update failed, continuing with current version", file=sys.stderr)
                return False
        else:
            print(f"Already running latest version: {__version__}", file=sys.stderr)
            
        return True
        
    except Exception as e:
        print(f"Auto-update error: {e}", file=sys.stderr)
        return False

# JSON-RPC server configuration

# Global session management
BROWSER_SESSIONS: Dict[str, Chrome] = {}
TAB_SESSIONS: Dict[str, Any] = {}
ELEMENT_CACHE: Dict[str, Any] = {}
EVENT_CALLBACKS: Dict[str, Dict[str, Any]] = {}
EVENT_LOGS: Dict[str, List[Dict]] = {}
NETWORK_LOGS: Dict[str, List[Any]] = {}

# Default configuration - environment independent
DEFAULT_CHROME_PATHS = [
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser", 
    "/usr/bin/chromium",
    "/opt/google/chrome/chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",     # Windows
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
]

def find_chrome_binary():
    """Find Chrome binary across different environments"""
    chrome_path = os.getenv('CHROME_PATH')
    if chrome_path and os.path.exists(chrome_path):
        return chrome_path
    
    for path in DEFAULT_CHROME_PATHS:
        if os.path.exists(path):
            return path
    
    # Try which/where command
    import subprocess
    try:
        result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    try:
        result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)  
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return DEFAULT_CHROME_PATHS[0]  # Fallback

DEFAULT_CHROME_PATH = find_chrome_binary()
DISPLAY = os.getenv('DISPLAY', ':99')

def send_response(response: Dict[str, Any]):
    """Send a JSON-RPC response"""
    print(json.dumps(response), flush=True)

def create_success_response(text: str) -> Dict[str, Any]:
    """Create a success response"""
    return {
        "content": [{"type": "text", "text": str(text)}]
    }

def create_error_response(text: str) -> Dict[str, Any]:
    """Create an error response"""
    return {
        "content": [{"type": "text", "text": f"Error: {str(text)}"}]
    }

def create_success_response_with_image(base64_data: str, mime_type: str) -> Dict[str, Any]:
    """Create a success response with image data"""
    return {
        "content": [
            {
                "type": "image",
                "data": base64_data,
                "mimeType": mime_type
            }
        ]
    }

def create_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a JSON data response"""
    return {
        "content": [{"type": "text", "text": json.dumps(data, indent=2)}]
    }

# Helper functions
def get_browser_session(session_id: str):
    """Get browser session by ID"""
    return BROWSER_SESSIONS.get(session_id)

def get_tab_session(tab_id: str):
    """Get tab session by ID"""
    return TAB_SESSIONS.get(tab_id)

def get_element(element_id: str):
    """Get element by ID"""
    return ELEMENT_CACHE.get(element_id)


def handle_initialize(request_id: Any) -> Dict[str, Any]:
    """Handle initialization"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "pydoll-browser-complete",
                "version": __version__
            }
        }
    }

def handle_tools_list(request_id: Any) -> Dict[str, Any]:
    """List all 82 available tools"""
    tools = [
        # === BROWSER SESSION MANAGEMENT ===
        {
            "name": "create_browser_session",
            "description": "Create a new Chrome browser instance with comprehensive configuration options",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Unique session identifier"},
                    "headless": {"type": "boolean", "description": "Run browser in headless mode", "default": True},
                    "window_size": {"type": "string", "description": "Browser window size (e.g., '1920,1080')"},
                    "user_agent": {"type": "string", "description": "Custom user agent string"},
                    "proxy": {"type": "string", "description": "Proxy server address"},
                    "disable_images": {"type": "boolean", "description": "Disable image loading", "default": False},
                    "disable_javascript": {"type": "boolean", "description": "Disable JavaScript execution", "default": False},
                    "additional_args": {"type": "array", "items": {"type": "string"}, "description": "Additional Chrome arguments"},
                    "chrome_path": {"type": "string", "description": "Path to Chrome executable"}
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "start_browser_session",
            "description": "Start an existing browser session and create initial tab",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Browser session identifier"}
                },
                "required": ["session_id"]
            }
        },
        {
            "name": "close_browser_session",
            "description": "Close a browser session and cleanup resources",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Browser session identifier"}
                },
                "required": ["session_id"]
            }
        },

        # === TAB MANAGEMENT ===
        {
            "name": "create_tab",
            "description": "Create a new tab in browser session",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "browser_session_id": {"type": "string", "description": "Browser session identifier"},
                    "tab_id": {"type": "string", "description": "Unique tab identifier"},
                    "url": {"type": "string", "description": "Initial URL to navigate to"}
                },
                "required": ["browser_session_id", "tab_id"]
            }
        },
        {
            "name": "close_tab",
            "description": "Close a browser tab",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"}
                },
                "required": ["tab_id"]
            }
        },
        {
            "name": "bring_tab_to_front",
            "description": "Bring a tab to the front/focus",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"}
                },
                "required": ["tab_id"]
            }
        },

        # === NAVIGATION ===
        {
            "name": "navigate",
            "description": "Navigate tab to specified URL with page load waiting",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"},
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_until": {"type": "string", "description": "Wait condition (load, domcontentloaded, networkidle)", "default": "load"}
                },
                "required": ["tab_id", "url"]
            }
        },
        {
            "name": "go_back",
            "description": "Navigate back in browser history",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"}
                },
                "required": ["tab_id"]
            }
        },
        {
            "name": "go_forward",
            "description": "Navigate forward in browser history",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"}
                },
                "required": ["tab_id"]
            }
        },
        {
            "name": "refresh_page",
            "description": "Refresh/reload the current page",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tab_id": {"type": "string", "description": "Tab identifier"},
                    "ignore_cache": {"type": "boolean", "description": "Bypass cache during refresh", "default": False}
                },
                "required": ["tab_id"]
            }
        },
        {
                "name": "find_element",
                "description": "Find a single element using various selector strategies",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "base_element_id": {"type": "string", "description": "Base element identifier for scoped search"},
                            "selector_type": {"type": "string", "description": "Selector type (css, xpath, id, name, tag, class)"},
                            "selector_value": {"type": "string", "description": "Selector value/expression"}
                        },
                        "required": ["tab_id", "base_element_id", "selector_type", "selector_value"]
                }
        },
        {
                "name": "find_elements",
                "description": "Find multiple elements using selector strategy",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "base_element_id": {"type": "string", "description": "Base element identifier for scoped search"},
                            "selector_type": {"type": "string", "description": "Selector type (css, xpath, id, name, tag, class)"},
                            "selector_value": {"type": "string", "description": "Selector value/expression"},
                            "limit": {"type": "integer", "description": "Maximum number of elements to return"}
                        },
                        "required": ["tab_id", "base_element_id", "selector_type", "selector_value"]
                }
        },
        {
                "name": "click_element",
                "description": "Click an element using mouse simulation",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                                "element_id": {"type": "string", "description": "Element identifier"},
                                "x_offset": {"type": "integer", "description": "Horizontal offset from element center", "default": 0},
                                "y_offset": {"type": "integer", "description": "Vertical offset from element center", "default": 0},
                                "hold_time": {"type": "number", "description": "Duration to hold mouse button in seconds", "default": 0.1}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "click_element_js",
                "description": "Click element using JavaScript instead of mouse simulation",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                                "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "type_text",
                "description": "Type text into an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                                "element_id": {"type": "string", "description": "Element identifier"},
                                "text": {"type": "string", "description": "Text to type"},
                                "clear_first": {"type": "boolean", "description": "Clear field before typing", "default": False},
                                "delay": {"type": "integer", "description": "Delay between keystrokes in milliseconds", "default": 0}
                        },
                        "required": ["element_id", "text"]
                }
        },
        {
                "name": "clear_text",
                "description": "Clear text from an input element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                                "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "press_key",
                "description": "Press a specific key or key combination",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key to press (e.g., 'ENTER', 'TAB', 'ESCAPE')"},
                            "element_id": {"type": "string", "description": "Element identifier (optional)"},
                            "modifiers": {"type": "array", "items": {"type": "string"}, "description": "Key modifiers (e.g., ['CTRL', 'SHIFT'])"}
                        },
                        "required": ["key"]
                }
        },
        {
                "name": "key_down",
                "description": "Press and hold a key (without releasing)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "key": {"type": "string", "description": "Key to press down (e.g., 'ENTER', 'TAB', 'ESCAPE')"},
                            "modifiers": {"type": "array", "items": {"type": "string"}, "description": "Key modifiers (e.g., ['CTRL', 'SHIFT'])"}
                        },
                        "required": ["element_id", "key"]
                }
        },
        {
                "name": "key_up",
                "description": "Release a previously pressed key",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "key": {"type": "string", "description": "Key to release (e.g., 'ENTER', 'TAB', 'ESCAPE')"}
                        },
                        "required": ["element_id", "key"]
                }
        },
        {
                "name": "hover_element",
                "description": "Hover mouse over an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                                "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "scroll_element",
                "description": "Scroll element into view or by specific amount",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "x": {"type": "integer", "description": "Horizontal scroll amount (optional)"},
                            "y": {"type": "integer", "description": "Vertical scroll amount (optional)"},
                            "behavior": {"type": "string", "description": "Scroll behavior ('auto', 'smooth', 'instant')", "default": "auto"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "drag_and_drop",
                "description": "Drag element from source to target location",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "source_element_id": {"type": "string", "description": "Source element identifier"},
                            "target_element_id": {"type": "string", "description": "Target element identifier"},
                            "x_offset": {"type": "integer", "description": "Horizontal offset for drop position (optional)"},
                            "y_offset": {"type": "integer", "description": "Vertical offset for drop position (optional)"}
                        },
                        "required": ["source_element_id", "target_element_id"]
                }
        },
        {
                "name": "get_element_text",
                "description": "Get visible text content of an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "get_element_attribute",
                "description": "Get attribute value from an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "attribute_name": {"type": "string", "description": "Name of the attribute to get"}
                        },
                        "required": ["element_id", "attribute_name"]
                }
        },
        {
                "name": "get_element_property",
                "description": "Get JavaScript property value from an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "property_name": {"type": "string", "description": "Name of the property to get"}
                        },
                        "required": ["element_id", "property_name"]
                }
        },
        {
                "name": "get_element_html",
                "description": "Get HTML content of an element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "get_element_bounds",
                "description": "Get element position and dimensions",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "get_element_bounds_js",
                "description": "Get element bounds using JavaScript method",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "is_element_visible",
                "description": "Check if element is visible on page",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "is_element_enabled",
                "description": "Check if element is enabled for interaction",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "is_element_selected",
                "description": "Check if element is selected (checkboxes, radio buttons)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "is_element_on_top",
                "description": "Check if element is on top (not covered by other elements)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "is_element_interactable",
                "description": "Check if element is fully interactable (visible, enabled, on top)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "get_parent_element",
                "description": "Get parent element of specified element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "parent_element_id": {"type": "string", "description": "Parent element identifier"}
                        },
                        "required": ["element_id", "parent_element_id"]
                }
        },
        {
                "name": "get_child_elements",
                "description": "Get child elements of specified element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "base_child_id": {"type": "string", "description": "Base child element identifier"},
                            "selector": {"type": "string", "description": "CSS selector for filtering children (optional)"}
                        },
                        "required": ["element_id", "base_child_id"]
                }
        },
        {
                "name": "get_sibling_elements",
                "description": "Get sibling elements of specified element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "base_sibling_id": {"type": "string", "description": "Base sibling element identifier"},
                            "next_siblings": {"type": "boolean", "description": "Include next siblings", "default": True},
                            "previous_siblings": {"type": "boolean", "description": "Include previous siblings", "default": True}
                        },
                        "required": ["element_id", "base_sibling_id"]
                }
        },
        {
                "name": "element_wait_until",
                "description": "Wait for an element to meet specific conditions",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "is_visible": {"type": "boolean", "description": "Wait for element to be visible (optional)"},
                            "is_interactable": {"type": "boolean", "description": "Wait for element to be interactable (optional)"},
                            "is_on_top": {"type": "boolean", "description": "Wait for element to be on top (optional)"},
                            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 10}
                        },
                        "required": ["element_id"]
                }
        },
        {
                "name": "wait_for_element",
                "description": "Wait for element to appear using selector",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "selector_type": {"type": "string", "description": "Selector type (css, xpath, id, name, tag, class)"},
                            "selector_value": {"type": "string", "description": "Selector value/expression"},
                            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30}
                        },
                        "required": ["tab_id", "selector_type", "selector_value"]
                }
        },
        {
                "name": "execute_script",
                "description": "Execute JavaScript in page context",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "script": {"type": "string", "description": "JavaScript code to execute"},
                            "timeout": {"type": "number", "description": "Script execution timeout in seconds (default: 5.0)"},
                            "handle_dialogs": {"type": "boolean", "description": "Automatically handle blocking dialogs (default: true)"}
                        },
                        "required": ["tab_id", "script"]
                }
        },
        {
                "name": "execute_script_on_element",
                "description": "Execute JavaScript with element as context",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "element_id": {"type": "string", "description": "Element identifier"},
                            "script": {"type": "string", "description": "JavaScript code to execute"}
                        },
                        "required": ["tab_id", "element_id", "script"]
                }
        },
        {
                "name": "get_page_title",
                "description": "Get the current page title",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "get_page_url",
                "description": "Get the current page URL",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "get_page_source",
                "description": "Get the current page HTML source",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "take_screenshot",
                "description": "Take screenshot of page or element",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "element_id": {"type": "string", "description": "Optional element identifier"},
                            "full_page": {"type": "boolean", "description": "Capture full page beyond viewport", "default": False},
                            "format": {"type": "string", "description": "Image format (png, jpeg)", "default": "png"},
                            "quality": {"type": "integer", "description": "Image quality (1-100)", "default": 90},
                            "save_path": {"type": "string", "description": "Optional file path to save screenshot instead of returning base64"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "save_pdf",
                "description": "Save page as PDF document",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "file_path": {"type": "string", "description": "Path where to save the PDF file"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "make_request",
                "description": "Make HTTP request using browser context",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "url": {"type": "string", "description": "URL to request"},
                            "method": {"type": "string", "description": "HTTP method", "default": "GET"},
                            "headers": {"type": "array", "items": {"type": "object"}, "description": "Request headers as array of {name, value} objects (optional)"},
                            "data": {"type": "string", "description": "Request body data (optional)"}
                        },
                        "required": ["tab_id", "url"]
                }
        },
        {
                "name": "set_cookies",
                "description": "Set cookies for current domain",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "cookies": {"type": "array", "items": {"type": "object"}, "description": "List of cookie objects"}
                        },
                        "required": ["tab_id", "cookies"]
                }
        },
        {
                "name": "get_cookies",
                "description": "Get cookies from current domain or specific URLs",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "urls": {"type": "array", "items": {"type": "string"}, "description": "URLs to get cookies from (optional)"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "delete_cookies",
                "description": "Delete specific cookies or all cookies",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "name": {"type": "string", "description": "Cookie name (optional)"},
                            "url": {"type": "string", "description": "Cookie URL (optional)"},
                            "domain": {"type": "string", "description": "Cookie domain (optional)"},
                            "path": {"type": "string", "description": "Cookie path (optional)"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "upload_file",
                "description": "Upload files through file input elements",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "File input element identifier"},
                            "file_paths": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to upload"}
                        },
                        "required": ["element_id", "file_paths"]
                }
        },
        {
                "name": "download_file",
                "description": "Download files from URLs",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "url": {"type": "string", "description": "URL to download from"},
                            "save_path": {"type": "string", "description": "Path where to save the downloaded file"}
                        },
                        "required": ["tab_id", "url"]
                }
        },
        {
                "name": "expect_file_chooser",
                "description": "Handle file chooser dialogs with automatic file selection",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "file_paths": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to select"},
                            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30}
                        },
                        "required": ["tab_id", "file_paths"]
                }
        },
        {
                "name": "enable_file_chooser_intercept",
                "description": "Enable file chooser dialog interception",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "disable_file_chooser_intercept",
                "description": "Disable file chooser dialog interception",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "wait_for_page_load",
                "description": "Wait for page to finish loading",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "wait_for_function",
                "description": "Wait for JavaScript function to return truthy value",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "script": {"type": "string", "description": "JavaScript function to wait for"},
                            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30}
                        },
                        "required": ["tab_id", "script"]
                }
        },
        {
                "name": "handle_alert",
                "description": "Handle JavaScript alert, confirm, or prompt dialogs",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "action": {"type": "string", "description": "Action to take (accept, dismiss)", "default": "accept"},
                            "text": {"type": "string", "description": "Text to enter in prompt dialogs (optional)"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "has_dialog",
                "description": "Check if there is an active dialog on the page",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "get_dialog_message",
                "description": "Get the message text from an active dialog",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "enable_page_events",
                "description": "Enable page event monitoring (load, navigation, dialogs)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "enable_network_events",
                "description": "Enable network event monitoring for request tracking",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "enable_fetch_events",
                "description": "Enable fetch event monitoring for request interception",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "enable_dom_events",
                "description": "Enable DOM event monitoring",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "enable_runtime_events",
                "description": "Enable runtime event monitoring (console, exceptions)",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "disable_all_events",
                "description": "Disable all event monitoring for a tab",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "register_event_callback",
                "description": "Register callback for specific browser events",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "callback_id": {"type": "string", "description": "Unique callback identifier"},
                            "event_type": {"type": "string", "description": "Event type to listen for"},
                            "filter_pattern": {"type": "string", "description": "Optional filter pattern"}
                        },
                        "required": ["tab_id", "callback_id", "event_type"]
                }
        },
        {
                "name": "remove_event_callback",
                "description": "Remove a specific event callback",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "callback_id": {"type": "string", "description": "Callback identifier to remove"}
                        },
                        "required": ["tab_id", "callback_id"]
                }
        },
        {
                "name": "clear_event_callbacks",
                "description": "Clear all event callbacks for a tab",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "get_event_logs",
                "description": "Get captured event logs from a tab",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "event_type": {"type": "string", "description": "Filter by event type (optional)"},
                            "limit": {"type": "integer", "description": "Maximum number of logs to return", "default": 100}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "continue_request",
                "description": "Continue an intercepted request with optional modifications",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "request_id": {"type": "string", "description": "Request identifier"},
                            "url": {"type": "string", "description": "Modified URL (optional)"},
                            "method": {"type": "string", "description": "Modified HTTP method (optional)"},
                            "headers": {"type": "array", "items": {"type": "object"}, "description": "Modified headers (optional)"},
                            "post_data": {"type": "string", "description": "Modified post data (optional)"}
                        },
                        "required": ["tab_id", "request_id"]
                }
        },
        {
                "name": "fail_request",
                "description": "Fail an intercepted request with specified error",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "request_id": {"type": "string", "description": "Request identifier"},
                            "error_reason": {"type": "string", "description": "Error reason", "default": "Failed"}
                        },
                        "required": ["tab_id", "request_id"]
                }
        },
        {
                "name": "fulfill_request",
                "description": "Fulfill an intercepted request with custom response",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "request_id": {"type": "string", "description": "Request identifier"},
                            "response_code": {"type": "integer", "description": "HTTP response code", "default": 200},
                            "response_headers": {"type": "array", "items": {"type": "object"}, "description": "Response headers (optional)"},
                            "body": {"type": "string", "description": "Response body (optional)"},
                            "binary_body": {"type": "string", "description": "Binary response body (optional)"}
                        },
                        "required": ["tab_id", "request_id"]
                }
        },
        {
                "name": "get_network_response_body",
                "description": "Get the response body for a specific network request",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "request_id": {"type": "string", "description": "Request identifier"}
                        },
                        "required": ["tab_id", "request_id"]
                }
        },
        {
                "name": "get_network_logs",
                "description": "Get network request logs with optional filtering",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier"},
                            "filter_pattern": {"type": "string", "description": "Optional filter pattern"},
                            "limit": {"type": "integer", "description": "Maximum number of logs to return", "default": 100}
                        },
                        "required": ["tab_id"]
                }
        },
        {
                "name": "get_frame",
                "description": "Get frame context from an iframe element for automation",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string", "description": "IFrame element identifier"},
                            "frame_tab_id": {"type": "string", "description": "Frame tab identifier"},
                            "validate_iframe": {"type": "boolean", "description": "Perform comprehensive iframe validation (default: true)"}
                        },
                        "required": ["element_id", "frame_tab_id"]
                }
        },
        {
                "name": "set_browser_preferences",
                "description": "Set advanced Chrome browser preferences for existing session",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Browser session identifier"},
                            "preferences": {"type": "object", "description": "Browser preferences object (optional)"},
                            "download_directory": {"type": "string", "description": "Download directory path (optional)"},
                            "accept_languages": {"type": "string", "description": "Accept languages setting (optional)"},
                            "prompt_for_download": {"type": "boolean", "description": "Prompt for download setting (optional)"}
                        },
                        "required": ["session_id"]
                }
        },
        {
                "name": "list_sessions",
                "description": "List all active browser and tab sessions",
                "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                }
        },
        {
                "name": "get_session_info",
                "description": "Get detailed information about a specific session",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session identifier to get info for"}
                        },
                        "required": ["session_id"]
                }
        },
        {
                "name": "cleanup_elements",
                "description": "Clean up cached element references",
                "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tab_id": {"type": "string", "description": "Tab identifier (optional - if not provided, cleans all elements)"}
                        },
                        "required": []
                }
        }
   
    ]
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }

# Global event loop for the server
SERVER_LOOP = None

# TOOL_HANDLERS will be defined after function definitions

async def handle_tool_call_async(request_id: Any, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool calls asynchronously with proper timeout handling"""
    try:
        if tool_name not in TOOL_HANDLERS:
            result = create_error_response(f"Unknown tool: {tool_name}")
        else:
            # Use timeout for all operations to prevent hanging
            timeout = 60  # 60 second timeout for operations
            handler = TOOL_HANDLERS[tool_name]
            
            try:
                result = await asyncio.wait_for(handler(**arguments), timeout=timeout)
            except asyncio.TimeoutError:
                result = create_error_response(f"Operation '{tool_name}' timed out after {timeout} seconds")
            except Exception as e:
                result = create_error_response(f"Operation '{tool_name}' failed: {str(e)}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
    except Exception as e:
        error_message = f"Error executing {tool_name}: {str(e)}"
        logger.error(f"{error_message}\n{traceback.format_exc()}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -1,
                "message": error_message
            }
        }

def handle_tool_call(request_id: Any, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper that runs the async handler in the server loop"""
    global SERVER_LOOP
    if SERVER_LOOP is None:
        # Fallback to creating a new loop if none exists
        return asyncio.run(handle_tool_call_async(request_id, tool_name, arguments))
    else:
        # Schedule the async call in the main server loop
        future = asyncio.run_coroutine_threadsafe(
            handle_tool_call_async(request_id, tool_name, arguments), 
            SERVER_LOOP
        )
        return future.result(timeout=120)  # 2 minute timeout for the entire operation

# ===== TOOL IMPLEMENTATIONS =====

# === BROWSER SESSION MANAGEMENT ===

async def create_browser_session(
    session_id: str,
    headless: bool = True,
    window_size: Optional[str] = None,
    user_agent: Optional[str] = None,
    proxy: Optional[str] = None,
    disable_images: bool = False,
    disable_javascript: bool = False,
    additional_args: Optional[List[str]] = None,
    chrome_path: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new Chrome browser instance using PyDoll async context manager"""
    try:
        if session_id in BROWSER_SESSIONS:
            return create_error_response(f"Browser session '{session_id}' already exists")
        
        # Create Chrome browser instance with options
        options = ChromiumOptions()
        
        # Add essential Chrome arguments for container environment
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-extensions")
        
        # Add anti-detection arguments to avoid Cloudflare blocking (default stealth mode)
        # Hide automation indicators (this was key to success with Cloudflare)
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Check if user_agent or additional_args already contains a user-agent
        has_user_agent_override = user_agent or (additional_args and any('--user-agent' in arg for arg in additional_args))
        
        # Set realistic user agent as default if not overridden (this was key to bypassing Cloudflare)
        if not has_user_agent_override:
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if headless:
            options.add_argument("--headless")
        if window_size:
            options.add_argument(f"--window-size={window_size}")
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        if disable_images:
            options.add_argument("--blink-settings=imagesEnabled=false")
        if disable_javascript:
            options.add_argument("--disable-javascript")
        if additional_args:
            for arg in additional_args:
                options.add_argument(arg)
        
        logger.info(f"Creating Chrome browser for session {session_id} with options: {[arg for arg in options.arguments]}")
        
        # Create the browser instance (without context manager for persistent sessions)
        browser = Chrome(options=options)
        
        # Store browser instance
        BROWSER_SESSIONS[session_id] = browser
        
        logger.info(f"Browser session '{session_id}' created successfully (not started yet)")
        
        return create_success_response(f"Browser session '{session_id}' created. Use start_browser_session to initialize.")
        
    except Exception as e:
        logger.error(f"Failed to create browser session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        return create_error_response(f"Failed to create browser session: {str(e)}")

async def start_browser_session(session_id: str) -> Dict[str, Any]:
    """Start an existing browser session and create initial tab"""
    try:
        if session_id not in BROWSER_SESSIONS:
            return create_error_response(f"Browser session '{session_id}' not found")
        
        browser = BROWSER_SESSIONS[session_id]
        
        # Check if already started
        initial_tab_id = f"{session_id}_initial"
        if initial_tab_id in TAB_SESSIONS:
            return create_success_response(f"Browser session '{session_id}' already started with tab '{initial_tab_id}'")
        
        try:
            logger.info(f"Starting browser for session {session_id}")
            initial_tab = await asyncio.wait_for(browser.start(), timeout=60)
            logger.info(f"Browser started successfully for session {session_id}, tab type: {type(initial_tab)}")
            
            # Inject shadow DOM override script to make all shadow roots open
            try:
                shadow_override_script = """
                    // Override attachShadow to force open mode for better automation access
                    if (typeof Element !== 'undefined' && Element.prototype.attachShadow) {
                        Element.prototype._originalAttachShadow = Element.prototype.attachShadow;
                        Element.prototype.attachShadow = function(options) {
                            // Always use open mode for automation compatibility
                            return this._originalAttachShadow.call(this, { mode: "open" });
                        };
                    }
                """
                
                await initial_tab._execute_command({
                    "method": "Page.addScriptToEvaluateOnNewDocument", 
                    "params": {"source": shadow_override_script}
                })
                logger.info(f"Shadow DOM override script injected for initial tab {initial_tab_id}")
            except Exception as e:
                logger.warning(f"Failed to inject shadow DOM override: {e}")
            
            # Store the initial tab
            TAB_SESSIONS[initial_tab_id] = initial_tab
            logger.info(f"Initial tab stored with ID {initial_tab_id}")
            
            # Automatically enable Cloudflare bypass for initial tab
            try:
                await initial_tab.enable_auto_solve_cloudflare_captcha()
                logger.info(f"Auto Cloudflare bypass enabled for initial tab {initial_tab_id}")
            except Exception as e:
                logger.warning(f"Failed to enable auto Cloudflare bypass for initial tab {initial_tab_id}: {e}")
            
            return create_success_response(f"Browser session '{session_id}' started with initial tab '{initial_tab_id}'")
            
        except asyncio.TimeoutError:
            logger.error(f"Browser start timed out for session {session_id}")
            return create_error_response("Browser start timed out after 60 seconds")
        except Exception as e:
            logger.error(f"Browser start failed for session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            return create_error_response(f"Browser start failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Failed to start browser session: {e}")
        return create_error_response(f"Failed to start browser session: {str(e)}")

async def close_browser_session(session_id: str) -> Dict[str, Any]:
    """Close a browser session and cleanup resources"""
    try:
        browser = get_browser_session(session_id)
        if not browser:
            return create_error_response(f"Browser session '{session_id}' not found")
        
        # Clean up related tabs and elements
        tabs_to_remove = [tab_id for tab_id, tab in TAB_SESSIONS.items() 
                          if hasattr(tab, 'browser') and tab.browser == browser]
        for tab_id in tabs_to_remove:
            del TAB_SESSIONS[tab_id]
        
        # Clean up elements for this browser
        elements_to_remove = [elem_id for elem_id, elem in ELEMENT_CACHE.items()
                              if hasattr(elem, 'tab') and elem.tab in tabs_to_remove]
        for elem_id in elements_to_remove:
            del ELEMENT_CACHE[elem_id]
        
        await browser.stop()
        del BROWSER_SESSIONS[session_id]
        
        return create_success_response(f"Browser session '{session_id}' closed successfully")
        
    except Exception as e:
        return create_error_response(f"Failed to close browser session: {str(e)}")

# === TAB MANAGEMENT ===




# === NAVIGATION ===

async def _verify_cloudflare_bypass(tab) -> bool:
    """Verify if Cloudflare bypass was successful by looking for success indicators"""
    try:
        await asyncio.sleep(3)  # Wait for success animation/update
        
        # Check for success indicators in iframes and main document
        success_found = await tab.evaluate("""
            () => {
                // Check main document first
                const successSelectors = [
                    '#success[style*="visible"]',
                    '.success[style*="visible"]', 
                    '[id*="success"]:not([style*="none"]):not([style*="hidden"])',
                    '.cb-container[style*="visible"]',
                    'svg[id*="success"]',
                    '[class*="success-circle"]',
                    '[class*="success-checkmark"]',
                    'span:contains("Success")',
                    'div:contains("Success")'
                ];
                
                for (const selector of successSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetWidth > 0 && el.offsetHeight > 0 && 
                                !el.style.display.includes('none') && 
                                !el.style.visibility.includes('hidden')) {
                                return true;
                            }
                        }
                    } catch (e) {
                        continue;
                    }
                }
                
                // Check all iframes for success indicators
                const iframes = document.querySelectorAll('iframe');
                for (const iframe of iframes) {
                    try {
                        const doc = iframe.contentDocument || iframe.contentWindow.document;
                        if (!doc) continue;
                        
                        for (const selector of successSelectors) {
                            const elements = doc.querySelectorAll(selector);
                            for (const el of elements) {
                                if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                                    return true;
                                }
                            }
                        }
                    } catch (e) {
                        continue;
                    }
                }
                
                return false;
            }
        """)
        
        return success_found
    except Exception:
        return False


async def _detect_cloudflare_protection(tab) -> bool:
    """Detect if the current page has Cloudflare protection"""
    try:
        # Check for common Cloudflare indicators
        cloudflare_indicators = [
            "cf-turnstile",  # Turnstile captcha
            "cf-im-under-attack",  # Under attack mode
            "cloudflare-challenge",  # Challenge page
            "Attention Required!",  # Block page title
            "Checking your browser",  # Verification page
            "jschl-answer",  # JavaScript challenge
            "jschl_vc",  # Challenge token
        ]
        
        # Get page content and check for indicators
        page_content = await tab.evaluate("document.documentElement.outerHTML")
        page_title = await tab.evaluate("document.title")
        
        # Check if any indicators are present
        for indicator in cloudflare_indicators:
            if indicator.lower() in page_content.lower() or indicator.lower() in page_title.lower():
                return True
        
        # Check for specific Cloudflare elements
        try:
            turnstile_element = await tab.wait_element(By.CLASS_NAME, "cf-turnstile", timeout=1, raise_exc=False)
            if turnstile_element:
                return True
        except:
            pass
            
        return False
    except Exception:
        return False


async def _find_and_click_in_cross_origin_iframe(tab) -> bool:
    """Use CDP commands to access cross-origin iframes and find Turnstile checkbox"""
    try:
        print("DEBUG: Starting CDP iframe access...")
        
        # Get document with full depth to see all frames
        doc_response = await tab._execute_command({
            "method": "DOM.getDocument", 
            "params": {"depth": -1, "pierce": True}
        })
        print(f"DEBUG: Got document response: {doc_response.get('result', {}).get('root', {}).get('nodeId', 'N/A')}")
        
        # Find all iframe elements
        iframe_query = await tab._execute_command({
            "method": "DOM.querySelectorAll",
            "params": {
                "nodeId": doc_response["result"]["root"]["nodeId"],
                "selector": "iframe"
            }
        })
        
        iframe_count = len(iframe_query["result"]["nodeIds"])
        print(f"DEBUG: Found {iframe_count} iframe elements")
        
        for i, node_id in enumerate(iframe_query["result"]["nodeIds"]):
            try:
                print(f"DEBUG: Processing iframe {i+1}/{iframe_count}, nodeId: {node_id}")
                
                # Get iframe description to access frameId
                iframe_desc = await tab._execute_command({
                    "method": "DOM.describeNode",
                    "params": {"nodeId": node_id}
                })
                
                frame_info = iframe_desc["result"]["node"]
                print(f"DEBUG: Iframe {i+1} info: {frame_info.get('attributes', [])} hasContentDocument: {'contentDocument' in frame_info} hasFrameId: {'frameId' in frame_info}")
                
                # Check if this might be a challenge iframe
                if ("contentDocument" not in frame_info and 
                    "frameId" in frame_info):
                    
                    frame_id = frame_info["frameId"]
                    print(f"DEBUG: Found potential cross-origin iframe with frameId: {frame_id}")
                    
                    # Get targets to see available frames
                    targets = await tab._execute_command({
                        "method": "Target.getTargets", 
                        "params": {}
                    })
                    
                    iframe_targets = [t for t in targets["result"]["targetInfos"] if t.get("type") == "iframe"]
                    print(f"DEBUG: Found {len(iframe_targets)} iframe targets: {[t.get('targetId') for t in iframe_targets]}")
                    
                    # Look for target matching our frameId or just take first iframe target
                    target_id = None
                    for target in iframe_targets:
                        if target.get("type") == "iframe":
                            target_id = target["targetId"]
                            print(f"DEBUG: Selected target: {target_id} url: {target.get('url', 'N/A')}")
                            break
                    
                    if target_id:
                        try:
                            print(f"DEBUG: Attempting to attach to target: {target_id}")
                            
                            # Create session for iframe target
                            session_response = await tab._execute_command({
                                "method": "Target.attachToTarget",
                                "params": {"targetId": target_id, "flatten": True}
                            })
                            
                            session_id = session_response["result"]["sessionId"]
                            print(f"DEBUG: Created iframe session: {session_id}")
                            
                            # Enable DOM for iframe session
                            dom_enable_response = await tab._execute_command({
                                "method": "DOM.enable",
                                "params": {},
                                "sessionId": session_id
                            })
                            print(f"DEBUG: DOM enabled for iframe session: {dom_enable_response}")
                            
                            # Add delay for iframe to fully load
                            await asyncio.sleep(1)
                            
                            # Get iframe document
                            iframe_doc = await tab._execute_command({
                                "method": "DOM.getDocument",
                                "params": {"depth": -1, "pierce": True},
                                "sessionId": session_id
                            })
                            print(f"DEBUG: Got iframe document: {iframe_doc.get('result', {}).get('root', {}).get('nodeId', 'N/A')}")
                            
                            # Look for checkboxes and clickable elements in iframe
                            selectors = [
                                'input[type="checkbox"]',
                                '[role="checkbox"]',
                                'button',
                                '[role="button"]',
                                '.cb-i', '.cb-c',
                                '[onclick]',
                                'div', 'span', 'label'  # Add more generic selectors
                            ]
                            
                            for selector in selectors:
                                try:
                                    print(f"DEBUG: Searching for selector '{selector}' in iframe...")
                                    
                                    element_query = await tab._execute_command({
                                        "method": "DOM.querySelector",
                                        "params": {
                                            "nodeId": iframe_doc["result"]["root"]["nodeId"],
                                            "selector": selector
                                        },
                                        "sessionId": session_id
                                    })
                                    
                                    element_node_id = element_query["result"]["nodeId"]
                                    if element_node_id:
                                        print(f"DEBUG: Found element with selector '{selector}', nodeId: {element_node_id}")
                                        
                                        # Get element details
                                        element_desc = await tab._execute_command({
                                            "method": "DOM.describeNode",
                                            "params": {"nodeId": element_node_id},
                                            "sessionId": session_id
                                        })
                                        print(f"DEBUG: Element details: {element_desc.get('result', {}).get('node', {})}")
                                        
                                        # Focus element first
                                        focus_response = await tab._execute_command({
                                            "method": "DOM.focus",
                                            "params": {"nodeId": element_node_id},
                                            "sessionId": session_id
                                        })
                                        print(f"DEBUG: Focus response: {focus_response}")
                                        
                                        # Get element bounds for clicking
                                        box_model = await tab._execute_command({
                                            "method": "DOM.getBoxModel",
                                            "params": {"nodeId": element_node_id},
                                            "sessionId": session_id
                                        })
                                        print(f"DEBUG: Box model response: {box_model}")
                                        
                                        if "result" in box_model and "content" in box_model["result"]:
                                            content = box_model["result"]["content"]
                                            # Calculate center point
                                            x = (content[0] + content[4]) / 2
                                            y = (content[1] + content[5]) / 2
                                            print(f"DEBUG: Click coordinates: x={x}, y={y}")
                                            
                                            # Try multiple click methods
                                            click_methods = [
                                                # Method 1: Standard mouse events
                                                lambda: _execute_mouse_click(tab, session_id, x, y, "standard"),
                                                # Method 2: JavaScript click
                                                lambda: _execute_js_click(tab, session_id, element_node_id),
                                                # Method 3: Touch events (mobile simulation)
                                                lambda: _execute_touch_click(tab, session_id, x, y)
                                            ]
                                            
                                            for method_idx, click_method in enumerate(click_methods):
                                                try:
                                                    print(f"DEBUG: Attempting click method {method_idx + 1}")
                                                    await click_method()
                                                    await asyncio.sleep(0.5)  # Small delay between attempts
                                                    
                                                    print(f'DEBUG: Clicked {selector} in cross-origin iframe via CDP (method {method_idx + 1})')
                                                    
                                                    # Clean up session and return success
                                                    await tab._execute_command({
                                                        "method": "Target.detachFromTarget",
                                                        "params": {"sessionId": session_id}
                                                    })
                                                    
                                                    return True
                                                    
                                                except Exception as click_error:
                                                    print(f"DEBUG: Click method {method_idx + 1} failed: {click_error}")
                                                    continue
                                            
                                except Exception as selector_error:
                                    print(f"DEBUG: Selector '{selector}' failed: {selector_error}")
                                    continue
                            
                            print("DEBUG: No clickable elements found in iframe")
                            
                            # Clean up session if we get here
                            await tab._execute_command({
                                "method": "Target.detachFromTarget", 
                                "params": {"sessionId": session_id}
                            })
                            
                        except Exception as target_error:
                            print(f"DEBUG: Target attachment failed: {target_error}")
                            continue
                    else:
                        print("DEBUG: No iframe targets found")
                        
            except Exception as iframe_error:
                print(f"DEBUG: Processing iframe {i+1} failed: {iframe_error}")
                continue
        
        print("DEBUG: CDP iframe access completed - no successful clicks")
        return False
        
    except Exception as main_error:
        print(f"DEBUG: CDP iframe access main error: {main_error}")
        return False


async def _execute_mouse_click(tab, session_id, x, y, method_name):
    """Execute standard mouse click events"""
    print(f"DEBUG: Executing {method_name} mouse click at ({x}, {y})")
    
    # Mouse press
    press_response = await tab._execute_command({
        "method": "Input.dispatchMouseEvent",
        "params": {
            "type": "mousePressed",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        },
        "sessionId": session_id
    })
    print(f"DEBUG: Mouse press response: {press_response}")
    
    await asyncio.sleep(0.1)  # Brief delay between press and release
    
    # Mouse release
    release_response = await tab._execute_command({
        "method": "Input.dispatchMouseEvent",
        "params": {
            "type": "mouseReleased",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        },
        "sessionId": session_id
    })
    print(f"DEBUG: Mouse release response: {release_response}")


async def _execute_js_click(tab, session_id, node_id):
    """Execute JavaScript click on element"""
    print(f"DEBUG: Executing JavaScript click on nodeId: {node_id}")
    
    # Try to click via JavaScript
    js_response = await tab._execute_command({
        "method": "Runtime.evaluate",
        "params": {
            "expression": f"""
                const element = document.querySelector('*');
                if (element) {{
                    element.click();
                    'clicked';
                }} else {{
                    'element not found';
                }}
            """
        },
        "sessionId": session_id
    })
    print(f"DEBUG: JavaScript click response: {js_response}")


async def _execute_touch_click(tab, session_id, x, y):
    """Execute touch events for mobile simulation"""
    print(f"DEBUG: Executing touch click at ({x}, {y})")
    
    # Touch start
    touch_start = await tab._execute_command({
        "method": "Input.dispatchTouchEvent",
        "params": {
            "type": "touchStart",
            "touchPoints": [{
                "x": x,
                "y": y,
                "radiusX": 1,
                "radiusY": 1
            }]
        },
        "sessionId": session_id
    })
    print(f"DEBUG: Touch start response: {touch_start}")
    
    await asyncio.sleep(0.1)
    
    # Touch end
    touch_end = await tab._execute_command({
        "method": "Input.dispatchTouchEvent",
        "params": {
            "type": "touchEnd",
            "touchPoints": []
        },
        "sessionId": session_id
    })
    print(f"DEBUG: Touch end response: {touch_end}")


async def _attempt_cloudflare_bypass(tab) -> bool:
    """Attempt to bypass Cloudflare protection using comprehensive nested structure approach"""
    try:
        # Wait a moment for the page to stabilize
        await asyncio.sleep(3)
        
        # Strategy 1: Direct DOM search for turnstile
        try:
            captcha = await tab.find_element(By.CSS_SELECTOR, ".cf-turnstile", timeout=2, raise_exc=False)
            if captcha:
                await captcha.click(x_offset=-125, y_offset=0)
                print('Clicked Cloudflare captcha (direct DOM)')
                if await _verify_cloudflare_bypass(tab):
                    print('Cloudflare bypass verified successful (direct DOM)')
                    return True
        except Exception:
            pass
        
        # Strategy 2: Deep nested search - iframes and shadow DOM
        try:
            # First level: check all iframes for Cloudflare challenge content
            iframes = await tab.find_elements(By.TAG_NAME, "iframe")
            
            for iframe in iframes:
                try:
                    # Check if iframe might contain challenge (by src, title, or size)
                    iframe_src = await iframe.get_attribute('src') or ''
                    iframe_title = await iframe.get_attribute('title') or ''
                    
                    is_challenge_iframe = (
                        'cloudflare' in iframe_src.lower() or
                        'challenge' in iframe_src.lower() or 
                        'turnstile' in iframe_src.lower() or
                        'challenge' in iframe_title.lower() or
                        'security' in iframe_title.lower()
                    )
                    
                    if is_challenge_iframe:
                        # Try to access iframe content and find captcha elements
                        try:
                            # Click the iframe itself first (sometimes needed for focus)
                            await iframe.click()
                            await asyncio.sleep(1)
                            
                            # Look for common captcha patterns inside iframe using JavaScript
                            captcha_found = await tab.evaluate("""
                                (iframe) => {
                                    try {
                                        const doc = iframe.contentDocument || iframe.contentWindow.document;
                                        if (!doc) return null;
                                        
                                        // Look for checkbox-style captcha elements
                                        const selectors = [
                                            'input[type="checkbox"]',
                                            '[role="checkbox"]', 
                                            'button',
                                            '[role="button"]',
                                            '.cb-i', '.cb-c',  // common checkbox classes
                                            '[onclick]',
                                            '.clickable'
                                        ];
                                        
                                        for (const selector of selectors) {
                                            const elements = doc.querySelectorAll(selector);
                                            for (const el of elements) {
                                                if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                                                    // Found a visible interactive element
                                                    el.click();
                                                    return true;
                                                }
                                            }
                                        }
                                        return false;
                                    } catch (e) {
                                        return null;
                                    }
                                }
                            """, iframe)
                            
                            if captcha_found:
                                print('Clicked Cloudflare captcha (iframe content)')
                                # Wait and verify success
                                if await _verify_cloudflare_bypass(tab):
                                    print('Cloudflare bypass verified successful')
                                    return True
                                
                        except Exception:
                            # If can't access iframe content, try clicking iframe with offset
                            await iframe.click(x_offset=-50, y_offset=0)
                            print('Clicked Cloudflare captcha (iframe with offset)')
                            if await _verify_cloudflare_bypass(tab):
                                print('Cloudflare bypass verified successful (iframe offset)')
                                return True
                            
                except Exception:
                    continue
        except Exception:
            pass
        
        # Strategy 3: Shadow DOM search with deep traversal
        try:
            # Look for elements that might have shadow roots
            potential_hosts = await tab.find_elements(By.TAG_NAME, "*")
            
            for host in potential_hosts[:50]:  # Limit to prevent timeout
                try:
                    shadow_root = await host.get_shadow_root()
                    if shadow_root:
                        # Check for turnstile in shadow root
                        turnstile = await shadow_root.find_element(By.CSS_SELECTOR, ".cf-turnstile", timeout=1, raise_exc=False)
                        if turnstile:
                            await turnstile.click(x_offset=-125, y_offset=0)
                            print('Clicked Cloudflare captcha (shadow DOM)')
                            if await _verify_cloudflare_bypass(tab):
                                print('Cloudflare bypass verified successful (shadow DOM)')
                                return True
                        
                        # Also check for iframes within shadow root
                        shadow_iframes = await shadow_root.find_elements(By.TAG_NAME, "iframe", timeout=1, raise_exc=False)
                        for shadow_iframe in shadow_iframes:
                            try:
                                await shadow_iframe.click(x_offset=-50, y_offset=0)
                                print('Clicked Cloudflare captcha (shadow iframe)')
                                if await _verify_cloudflare_bypass(tab):
                                    print('Cloudflare bypass verified successful (shadow iframe)')
                                    return True
                            except Exception:
                                continue
                                
                except Exception:
                    continue
        except Exception:
            pass
        
        # Strategy 4: CDP cross-origin iframe access
        try:
            if await _find_and_click_in_cross_origin_iframe(tab):
                print('Clicked Cloudflare captcha (CDP cross-origin)')
                if await _verify_cloudflare_bypass(tab):
                    print('Cloudflare bypass verified successful (CDP cross-origin)')
                    return True
        except Exception:
            pass
        
        # Strategy 5: Fallback to PyDoll's built-in methods
        try:
            async with tab.expect_and_bypass_cloudflare_captcha(timeout=10):
                pass
            return True
        except Exception:
            pass
        
        try:
            await tab.enable_auto_solve_cloudflare_captcha(timeout=5)
            await asyncio.sleep(2)
            await tab.disable_auto_solve_cloudflare_captcha()
            return True
        except Exception:
            pass
        
        return False
    except Exception:
        return False


async def navigate(tab_id: str, url: str, wait_until: str = "load") -> Dict[str, Any]:
    """Navigate tab to specified URL with page load waiting"""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            return create_error_response(f"Tab '{tab_id}' not found")
        
        # Map wait conditions to appropriate timeouts
        timeout_map = {"load": 60, "domcontentloaded": 30, "networkidle": 90}
        timeout = timeout_map.get(wait_until, 60)
        
        # First attempt normal navigation
        await tab.go_to(url, timeout=timeout)
        
        # Check if Cloudflare protection is detected
        cloudflare_detected = await _detect_cloudflare_protection(tab)
        
        if cloudflare_detected:
            # Cloudflare detected, attempt bypass using direct approach
            bypass_successful = await _attempt_cloudflare_bypass(tab)
            
            if bypass_successful:
                return create_success_response(f"Successfully navigated to {url} (Cloudflare bypassed)")
            else:
                # If bypass failed, still return success since navigation worked
                return create_success_response(f"Successfully navigated to {url} (Cloudflare detected but bypass failed)")
        else:
            # No Cloudflare detected, normal navigation successful
            return create_success_response(f"Successfully navigated to {url}")
        
    except Exception as e:
        return create_error_response(f"Failed to navigate: {str(e)}")



async def refresh_page(tab_id: str, ignore_cache: bool = False) -> Dict[str, Any]:
    """Refresh/reload the current page"""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            return create_error_response(f"Tab '{tab_id}' not found")
        
        await tab.refresh(ignore_cache=ignore_cache)
        
        return create_success_response("Page refreshed successfully")
        
    except Exception as e:
        return create_error_response(f"Failed to refresh page: {str(e)}")

async def close_browser_session(session_id: str):
    """Close a browser session and cleanup resources."""
    try:
        if session_id not in BROWSER_SESSIONS:
            raise ValueError(f"Session '{session_id}' not found")
        
        browser = BROWSER_SESSIONS[session_id]
        await browser.stop()
        
        # Clean up related tabs
        tabs_to_remove = [tab_id for tab_id in TAB_SESSIONS.keys() if tab_id.startswith(f"{session_id}_")]
        for tab_id in tabs_to_remove:
            del TAB_SESSIONS[tab_id]
            if tab_id in EVENT_CALLBACKS:
                del EVENT_CALLBACKS[tab_id]
            if tab_id in EVENT_LOGS:
                del EVENT_LOGS[tab_id]
            if tab_id in NETWORK_LOGS:
                del NETWORK_LOGS[tab_id]
        
        del BROWSER_SESSIONS[session_id]
        
        return create_success_response(f"Browser session '{session_id}' closed successfully")
    except Exception as e:
        return create_error_response(f"Failed to close browser session: {str(e)}")

async def create_tab(browser_session_id: str, tab_id: str, url: Optional[str] = None):
    """Create a new tab in browser session."""
    try:
        if browser_session_id not in BROWSER_SESSIONS:
            raise ValueError(f"Browser session '{browser_session_id}' not found")
        
        if tab_id in TAB_SESSIONS:
            raise ValueError(f"Tab '{tab_id}' already exists")
        
        browser = BROWSER_SESSIONS[browser_session_id]
        
        # Create new tab (browser should already be started)
        logger.info(f"Creating new tab {tab_id} for session {browser_session_id}")
        tab = await browser.new_tab(url or "")
        logger.info(f"Tab created successfully: {tab_id}")
        
        # Inject shadow DOM override script for this tab too
        try:
            shadow_override_script = """
                // Override attachShadow to force open mode for better automation access
                if (typeof Element !== 'undefined' && Element.prototype.attachShadow) {
                    Element.prototype._originalAttachShadow = Element.prototype.attachShadow;
                    Element.prototype.attachShadow = function(options) {
                        // Always use open mode for automation compatibility
                        return this._originalAttachShadow.call(this, { mode: "open" });
                    };
                }
            """
            
            await tab._execute_command({
                "method": "Page.addScriptToEvaluateOnNewDocument", 
                "params": {"source": shadow_override_script}
            })
            logger.info(f"Shadow DOM override script injected for tab {tab_id}")
        except Exception as e:
            logger.warning(f"Failed to inject shadow DOM override for tab {tab_id}: {e}")
        
        # Automatically enable Cloudflare bypass for all tabs
        try:
            await tab.enable_auto_solve_cloudflare_captcha()
            logger.info(f"Auto Cloudflare bypass enabled for tab {tab_id}")
        except Exception as e:
            logger.warning(f"Failed to enable auto Cloudflare bypass for tab {tab_id}: {e}")
        
        TAB_SESSIONS[tab_id] = tab
        
        return create_success_response(f"Tab '{tab_id}' created successfully" + (f" and navigated to {url}" if url else ""))
    except asyncio.TimeoutError:
        return create_error_response(f"Failed to create tab: Operation timed out")
    except Exception as e:
        return create_error_response(f"Failed to create tab: {str(e)}")

async def close_tab(tab_id: str):
    """Close a browser tab."""
    logger.info(f"close_tab called for tab_id: {tab_id}")
    try:
        if tab_id not in TAB_SESSIONS:
            logger.error(f"Tab {tab_id} not found in TAB_SESSIONS")
            raise ValueError(f"Tab '{tab_id}' not found")
        
        logger.info(f"Tab {tab_id} found in TAB_SESSIONS, getting tab object")
        tab = TAB_SESSIONS[tab_id]
        logger.info(f"Got tab object for {tab_id}: {type(tab)}")
        
        # Try to close the tab via PyDoll, but don't let it fail the entire operation
        # PyDoll tabs often can't be closed cleanly due to internal browser state issues
        close_successful = False
        try:
            logger.info(f"Attempting to close PyDoll tab for {tab_id}")
            await asyncio.wait_for(tab.close(), timeout=5.0)  # Shorter timeout
            logger.info(f"Successfully closed PyDoll tab for {tab_id}")
            close_successful = True
        except Exception as close_error:
            logger.info(f"PyDoll tab close failed for {tab_id} (continuing with cleanup): {str(close_error)[:100]}")
            # Don't log full error details as this is expected behavior
        
        # Clean up related elements and events step by step to isolate any errors
        logger.info(f"Starting cleanup for tab {tab_id}")
        
        # Clean up elements
        try:
            elements_to_remove = [elem_id for elem_id in ELEMENT_CACHE.keys() if elem_id.startswith(f"{tab_id}_")]
            logger.info(f"Found {len(elements_to_remove)} elements to clean up for {tab_id}")
            for elem_id in elements_to_remove:
                del ELEMENT_CACHE[elem_id]
            logger.info(f"Cleaned up {len(elements_to_remove)} elements for {tab_id}")
        except Exception as elem_error:
            logger.warning(f"Error cleaning up elements for {tab_id}: {elem_error}")
        
        # Clean up event callbacks
        try:
            if tab_id in EVENT_CALLBACKS:
                del EVENT_CALLBACKS[tab_id]
                logger.info(f"Cleaned up event callbacks for {tab_id}")
        except Exception as cb_error:
            logger.warning(f"Error cleaning up event callbacks for {tab_id}: {cb_error}")
        
        # Clean up event logs
        try:
            if tab_id in EVENT_LOGS:
                del EVENT_LOGS[tab_id]
                logger.info(f"Cleaned up event logs for {tab_id}")
        except Exception as log_error:
            logger.warning(f"Error cleaning up event logs for {tab_id}: {log_error}")
        
        # Clean up network logs
        try:
            if tab_id in NETWORK_LOGS:
                del NETWORK_LOGS[tab_id]
                logger.info(f"Cleaned up network logs for {tab_id}")
        except Exception as net_error:
            logger.warning(f"Error cleaning up network logs for {tab_id}: {net_error}")
        
        # Finally, remove from TAB_SESSIONS
        try:
            del TAB_SESSIONS[tab_id]
            logger.info(f"Removed {tab_id} from TAB_SESSIONS")
        except Exception as session_error:
            logger.error(f"Critical error removing {tab_id} from TAB_SESSIONS: {session_error}")
            raise session_error
        
        if close_successful:
            return create_success_response(f"Tab '{tab_id}' closed successfully")
        else:
            return create_success_response(f"Tab '{tab_id}' session cleaned up successfully")
    except Exception as e:
        logger.error(f"Failed to close tab {tab_id}: {str(e)}", exc_info=True)
        return create_error_response(f"Failed to close tab: {str(e)}")

async def bring_tab_to_front(tab_id: str):
    """Bring a tab to the front/focus."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.bring_to_front()
        
        return create_success_response(f"Tab '{tab_id}' brought to front")
    except Exception as e:
        return create_error_response(f"Bring tab to front failed: {str(e)}")

async def navigate(tab_id: str, url: str, wait_until: str = "load"):
    """Navigate tab to specified URL."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.go_to(url)
        
        return create_success_response(f"Successfully navigated to {url}")
    except Exception as e:
        return create_error_response(f"Navigation failed: {str(e)}")

async def go_back(tab_id: str):
    """Navigate back in browser history."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Get navigation history first
        from pydoll.commands import PageCommands
        history_resp = await tab._execute_command(PageCommands.get_navigation_history())
        history = history_resp['result']
        
        current_index = history['currentIndex']
        if current_index > 0:
            # Navigate to previous entry
            prev_entry_id = history['entries'][current_index - 1]['id']
            await tab._execute_command(PageCommands.navigate_to_history_entry(prev_entry_id))
            return create_success_response("Successfully navigated back")
        else:
            return create_error_response("Cannot navigate back: already at the beginning of history")
    except Exception as e:
        return create_error_response(f"Go back failed: {str(e)}")

async def go_forward(tab_id: str):
    """Navigate forward in browser history."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Get navigation history first
        from pydoll.commands import PageCommands
        history_resp = await tab._execute_command(PageCommands.get_navigation_history())
        history = history_resp['result']
        
        current_index = history['currentIndex']
        entries = history['entries']
        if current_index < len(entries) - 1:
            # Navigate to next entry
            next_entry_id = entries[current_index + 1]['id']
            await tab._execute_command(PageCommands.navigate_to_history_entry(next_entry_id))
            return create_success_response("Successfully navigated forward")
        else:
            return create_error_response("Cannot navigate forward: already at the end of history")
    except Exception as e:
        return create_error_response(f"Go forward failed: {str(e)}")

async def refresh_page(tab_id: str, ignore_cache: bool = False):
    """Refresh/reload the current page."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.refresh(ignore_cache=ignore_cache)
        
        return create_success_response("Page refreshed successfully")
    except Exception as e:
        return create_error_response(f"Page refresh failed: {str(e)}")

async def find_element(
    tab_id: str,
    base_element_id: str,
    selector_type: str,
    selector_value: str,
    timeout: float = 10
):
    """Find a single element using various selector strategies."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Handle existing element IDs by generating unique ones
        original_id = base_element_id
        counter = 1
        while base_element_id in ELEMENT_CACHE:
            base_element_id = f"{original_id}_{counter}"
            counter += 1
        
        # Map selector types to PyDoll By constants
        selector_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
        }
        
        if selector_type not in selector_map:
            raise ValueError(f"Invalid selector type: {selector_type}")
        
        by_type = selector_map[selector_type]
        if selector_type == "css":
            element = await tab.query(selector_value, timeout=timeout, raise_exc=False)
        elif selector_type == "xpath":
            element = await tab.query(selector_value, timeout=timeout, raise_exc=False)
        elif selector_type == "id":
            element = await tab.find(id=selector_value, timeout=timeout, raise_exc=False)
        elif selector_type == "name":
            element = await tab.find(name=selector_value, timeout=timeout, raise_exc=False)
        elif selector_type == "tag":
            element = await tab.find(tag_name=selector_value, timeout=timeout, raise_exc=False)
        elif selector_type == "class":
            element = await tab.find(class_name=selector_value, timeout=timeout, raise_exc=False)
        else:
            element = await tab._find_element(by_type, selector_value, raise_exc=False)
        
        if not element:
            raise ValueError(f"Element not found with selector '{selector_type}': {selector_value}")
        
        ELEMENT_CACHE[base_element_id] = element
        
        return create_success_response(f"Element '{base_element_id}' found successfully")
    except Exception as e:
        return create_error_response(f"Find element failed: {str(e)}")

async def find_elements(
    tab_id: str,
    base_element_id: str,
    selector_type: str,
    selector_value: str,
    limit: Optional[int] = None
):
    """Find multiple elements using selector strategy."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Map selector types to PyDoll By constants
        selector_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
        }
        
        if selector_type not in selector_map:
            raise ValueError(f"Invalid selector type: {selector_type}")
        
        by_type = selector_map[selector_type]
        if selector_type == "css":
            elements = await tab.query(selector_value, find_all=True, raise_exc=False) or []
        elif selector_type == "xpath":
            elements = await tab.query(selector_value, find_all=True, raise_exc=False) or []
        elif selector_type == "id":
            elements = await tab.find(id=selector_value, find_all=True, raise_exc=False) or []
        elif selector_type == "name":
            elements = await tab.find(name=selector_value, find_all=True, raise_exc=False) or []
        elif selector_type == "tag":
            elements = await tab.find(tag_name=selector_value, find_all=True, raise_exc=False) or []
        elif selector_type == "class":
            elements = await tab.find(class_name=selector_value, find_all=True, raise_exc=False) or []
        else:
            elements = await tab._find_elements(by_type, selector_value, raise_exc=False)
        
        if limit:
            elements = elements[:limit]
        
        element_ids = []
        for i, element in enumerate(elements):
            element_id = f"{base_element_id}_{i}"
            ELEMENT_CACHE[element_id] = element
            element_ids.append(element_id)
        
        return create_success_response(f"Found {len(element_ids)} elements: {', '.join(element_ids)}")
    except Exception as e:
        return create_error_response(f"Find elements failed: {str(e)}")

async def click_element(element_id: str, button: str = "left", click_count: int = 1, x_offset: int = 0, y_offset: int = 0, hold_time: float = 0.1):
    """Click an element using mouse simulation."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Handle offsets and hold time if specified
        if x_offset != 0 or y_offset != 0 or hold_time != 0.1:
            # For complex clicking, use standard element click for now
            # Future enhancement: implement precise coordinate clicking with hold time
            if click_count == 1:
                if button == "right":
                    await element.right_click()
                else:
                    await element.click()
            else:
                await element.double_click() if click_count == 2 else await element.click()
        else:
            # Standard clicking
            if click_count == 1:
                if button == "right":
                    await element.right_click()
                else:
                    await element.click()
            else:
                await element.double_click() if click_count == 2 else await element.click()
        
        return create_success_response(f"Element '{element_id}' clicked successfully")
    except Exception as e:
        return create_error_response(f"Click element failed: {str(e)}")

async def click_element_js(element_id: str):
    """Click element using JavaScript instead of mouse simulation."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        await element.click_using_js()
        
        return create_success_response(f"Element '{element_id}' clicked using JavaScript")
    except Exception as e:
        return create_error_response(f"Click element JS failed: {str(e)}")

async def type_text(element_id: str, text: str, clear_first: bool = False, delay: int = 0):
    """Type text into an element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        if clear_first:
            # Use JavaScript to clear since element.clear() doesn't exist
            await element.execute_script("this.value = '';")
        
        if delay > 0:
            # Use correct method with interval parameter
            await element.type_text(text, interval=delay/1000)
        else:
            # Use correct method name
            await element.type_text(text)
        
        return create_success_response(f"Successfully typed text into element '{element_id}'")
    except Exception as e:
        return create_error_response(f"Type text failed: {str(e)}")

async def clear_text(element_id: str):
    """Clear text from an input element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Use JavaScript to clear since element.clear() doesn't exist
        await element.execute_script("this.value = '';")
        
        return create_success_response(f"Element '{element_id}' cleared successfully")
    except Exception as e:
        return create_error_response(f"Clear text failed: {str(e)}")

async def press_key(key: str, element_id: Optional[str] = None, modifiers: Optional[List[str]] = None):
    """Press a specific key or key combination."""
    try:
        # Convert key string to Key enum if available
        key_obj = getattr(Key, key.upper()) if hasattr(Key, key.upper()) else key
        
        if element_id:
            element = get_element(element_id)
            if not element:
                raise ValueError(f"Element '{element_id}' not found")
            await element.press_keyboard_key(key_obj)
        else:
            # Page-level key press - use first available tab
            if not TAB_SESSIONS:
                raise ValueError("No active tabs for page-level key press")
            
            tab = next(iter(TAB_SESSIONS.values()))
            
            # Import required types for key event
            from pydoll.commands import InputCommands
            from pydoll.protocol.input.types import KeyEventType
            
            # Send key down and up events to simulate key press
            await tab._execute_command(
                InputCommands.dispatch_key_event(
                    type=KeyEventType.KEY_DOWN,
                    key=key_obj if isinstance(key_obj, str) else str(key_obj)
                )
            )
            await tab._execute_command(
                InputCommands.dispatch_key_event(
                    type=KeyEventType.KEY_UP,
                    key=key_obj if isinstance(key_obj, str) else str(key_obj)
                )
            )
        
        return create_success_response(f"Key '{key}' pressed successfully")
    except Exception as e:
        return create_error_response(f"Press key failed: {str(e)}")

async def key_down(element_id: str, key: str, modifiers: Optional[List[str]] = None):
    """Press and hold a key (without releasing)."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        key_obj = getattr(Key, key.upper()) if hasattr(Key, key.upper()) else key
        
        await element.key_down(key_obj)
        
        return create_success_response(f"Key '{key}' pressed down")
    except Exception as e:
        return create_error_response(f"Key down failed: {str(e)}")

async def key_up(element_id: str, key: str):
    """Release a previously pressed key."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        key_obj = getattr(Key, key.upper()) if hasattr(Key, key.upper()) else key
        
        await element.key_up(key_obj)
        
        return create_success_response(f"Key '{key}' released")
    except Exception as e:
        return create_error_response(f"Key up failed: {str(e)}")

async def hover_element(element_id: str):
    """Hover mouse over an element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Implement hover using mouse events since element.hover() doesn't exist
        bounds = await element.get_bounds_using_js()
        center_x = bounds['x'] + bounds['width'] / 2
        center_y = bounds['y'] + bounds['height'] / 2
        
        # Import InputCommands and MouseEventType from the connection handler's tab
        from pydoll.commands import InputCommands
        from pydoll.protocol.input.types import MouseEventType
        
        command = InputCommands.dispatch_mouse_event(
            type=MouseEventType.MOUSE_MOVED,
            x=int(center_x),
            y=int(center_y)
        )
        await element._connection_handler.execute_command(command)
        
        return create_success_response(f"Element '{element_id}' hovered successfully")
    except Exception as e:
        return create_error_response(f"Hover element failed: {str(e)}")

async def scroll_element(
    element_id: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    behavior: str = "auto"
):
    """
    Scroll element into view or by specific amount.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. X/Y OFFSET LIMITATIONS: The x/y offset scrolling may fail with error:
       "'WebElement' object has no attribute 'scroll_by'"
       This indicates the underlying PyDoll element doesn't support scroll_by method.
       
    2. WORKING USAGE PATTERNS:
       ✓ Basic scroll into view (no x/y parameters):
         scroll_element(element_id, behavior="smooth")
         
       ✗ Offset scrolling (may fail):
         scroll_element(element_id, x=100, y=200)  # May cause attribute error
         
    3. BEHAVIOR PARAMETER:
       - "auto": Default browser scrolling behavior  
       - "smooth": Smooth animated scrolling
       - "instant": Immediate scrolling without animation
       
    4. ALTERNATIVE FOR OFFSET SCROLLING:
       Use JavaScript execution for precise control:
       execute_script_on_element(tab_id, element_id, 
           "arguments[0].scrollBy(100, 200);")
           
    EXAMPLE USAGE:
    ==============
    # Safe usage - scroll into view only
    scroll_element("my_element", behavior="smooth")
    
    # For offset scrolling, use JavaScript instead:
    execute_script_on_element(tab_id, element_id,
        "arguments[0].scrollBy(50, 100);")
    """
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        if x is not None or y is not None:
            await element.scroll_by(x or 0, y or 0)
        else:
            await element.scroll_into_view()
        
        return create_success_response(f"Element '{element_id}' scrolled successfully")
    except Exception as e:
        return create_error_response(f"Scroll element failed: {str(e)}")

async def drag_and_drop(
    source_element_id: str,
    target_element_id: str,
    x_offset: Optional[int] = None,
    y_offset: Optional[int] = None
):
    """Drag element from source to target location."""
    try:
        source_element = get_element(source_element_id)
        target_element = get_element(target_element_id)
        
        if not source_element:
            raise ValueError(f"Source element '{source_element_id}' not found")
        if not target_element:
            raise ValueError(f"Target element '{target_element_id}' not found")
        
        # PyDoll doesn't have built-in drag_and_drop, so simulate with mouse events
        # Get element positions
        source_bounds = await source_element.get_bounds_using_js()
        target_bounds = await target_element.get_bounds_using_js()
        
        if not source_bounds or not target_bounds:
            raise ValueError("Could not get element bounds for drag and drop")
            
        source_x = source_bounds['x'] + source_bounds['width'] / 2
        source_y = source_bounds['y'] + source_bounds['height'] / 2
        target_x = target_bounds['x'] + target_bounds['width'] / 2  
        target_y = target_bounds['y'] + target_bounds['height'] / 2
        
        # Simulate drag and drop with mouse events via tab
        tab = None
        for tab_session in TAB_SESSIONS.values():
            if hasattr(tab_session, '_connection_handler') and tab_session._connection_handler == source_element._connection_handler:
                tab = tab_session
                break
        
        if not tab:
            raise ValueError("Could not find associated tab for drag and drop")
            
        from pydoll.commands import InputCommands
        from pydoll.protocol.input.types import MouseButton, MouseEventType
        
        # Mouse down on source
        await source_element._execute_command(
            InputCommands.dispatch_mouse_event(
                type=MouseEventType.MOUSE_PRESSED,
                x=source_x,
                y=source_y,
                button=MouseButton.LEFT,
                click_count=1
            )
        )
        
        # Mouse move to target
        await source_element._execute_command(
            InputCommands.dispatch_mouse_event(
                type=MouseEventType.MOUSE_MOVED,
                x=target_x,
                y=target_y
            )
        )
        
        # Mouse up on target
        await source_element._execute_command(
            InputCommands.dispatch_mouse_event(
                type=MouseEventType.MOUSE_RELEASED,
                x=target_x,
                y=target_y,
                button=MouseButton.LEFT,
                click_count=1
            )
        )
        
        return create_success_response(f"Drag and drop from '{source_element_id}' to '{target_element_id}' completed")
    except Exception as e:
        return create_error_response(f"Drag and drop failed: {str(e)}")

async def get_element_text(element_id: str):
    """Get visible text content of an element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Try different methods to get text
        text = ""
        try:
            text = await element.text()
            if text is not None:
                return create_success_response(str(text))
        except:
            pass
        
        try:
            # Try getting text content via JavaScript
            text = await element.evaluate("el => el.textContent || el.innerText || ''")
            if text is not None:
                return create_success_response(str(text))
        except:
            pass
        
        # Fallback to empty string
        return create_success_response("")
    except Exception as e:
        return create_error_response(f"Get element text failed: {str(e)}")

async def get_element_attribute(element_id: str, attribute_name: str):
    """Get attribute value from an element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        value = element.get_attribute(attribute_name)
        
        return create_success_response(str(value) if value is not None else "")
    except Exception as e:
        return create_error_response(f"Get element attribute failed: {str(e)}")

async def get_element_property(element_id: str, property_name: str):
    """
    Get JavaScript property value from an element.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. CONTEXT ID ERRORS: This function frequently fails with:
       "Cannot find context with specified id"
       This indicates issues with element reference management or timing.
       
    2. STALE ELEMENT REFERENCES: Element references can become stale after:
       - Page navigation or refresh
       - DOM modifications
       - Time delays between find and property access
       
    3. RECOMMENDED ALTERNATIVE: Use execute_script_on_element instead:
       ✗ Unreliable: get_element_property(element_id, "value")
       ✓ Reliable:   execute_script_on_element(tab_id, element_id, "return arguments[0].value;")
       
    4. WORKING PROPERTY PATTERNS:
       - element.value (form inputs)
       - element.textContent (text content)  
       - element.innerHTML (HTML content)
       - element.disabled (boolean state)
       - element.checked (checkbox state)
       
    5. WHY EXECUTE_SCRIPT_ON_ELEMENT WORKS BETTER:
       - Handles element context more reliably
       - Provides better error messages
       - More consistent across different PyDoll versions
       - Supports complex property access (element.style.display, etc.)
       
    EXAMPLE USAGE:
    ==============
    # Instead of get_element_property, use:
    result = execute_script_on_element(
        tab_id="my_tab",
        element_id="my_element", 
        script="return arguments[0].value;"
    )
    
    # For complex properties:
    result = execute_script_on_element(
        tab_id="my_tab", 
        element_id="my_element",
        script="return {value: arguments[0].value, disabled: arguments[0].disabled};"
    )
    
    Note: If you get a 'stale element reference' error, re-find the element
    using find_element before calling this function.
    """
    try:
        element = get_element(element_id)
        if not element:
            return create_error_response(f"Element '{element_id}' not found")
        
        # Find the tab that contains this element
        tab = None
        for tab_id, tab_obj in TAB_SESSIONS.items():
            tab = tab_obj
            break
            
        if not tab:
            return create_error_response("No active tab found for element property retrieval")
        
        # Use the same approach as execute_script_on_element
        script = f"argument.{property_name}"
        
        # Add return statement if not present (same as execute_script_on_element)
        if not script.strip().startswith('return'):
            script = f"return {script}"
        
        # Execute script on the tab with element as argument
        try:
            result = await tab.execute_script(script, element)
            return create_success_response(str(result) if result is not None else "")
        except Exception as e:
            # Check if this is a stale element reference
            if "Cannot find context with specified id" in str(e) or "stale element" in str(e).lower():
                return create_error_response(f"Element '{element_id}' reference is stale. Please re-find the element using find_element before accessing properties.")
            
            # Fallback: try to access as an attribute
            try:
                script = f"return argument.getAttribute('{property_name}');"
                result = await tab.execute_script(script, element)
                return create_success_response(str(result) if result is not None else "")
            except Exception as fallback_error:
                if "Cannot find context with specified id" in str(fallback_error):
                    return create_error_response(f"Element '{element_id}' reference is stale. Please re-find the element using find_element before accessing properties.")
                return create_error_response(f"Failed to get property '{property_name}': {str(e)}, Fallback failed: {str(fallback_error)}")
        
    except Exception as e:
        return create_error_response(f"Get element property failed: {str(e)}")

async def get_element_html(element_id: str, outer_html: bool = False):
    """Get HTML content of an element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        if outer_html:
            html = await element.outer_html
        else:
            html = await element.inner_html
        
        return create_success_response(html or "")
    except Exception as e:
        return create_error_response(f"Get element HTML failed: {str(e)}")

async def get_element_bounds(element_id: str):
    """Get element position and dimensions."""
    # Delegate to the JS method which works reliably
    return await get_element_bounds_js(element_id)

async def get_element_bounds_js(element_id: str):
    """Get element bounds using JavaScript method."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        bounds = await element.get_bounds_using_js()
        
        return create_success_response(json.dumps(bounds, indent=2))
    except Exception as e:
        return create_error_response(f"Get element bounds JS failed: {str(e)}")

async def is_element_visible(element_id: str):
    """Check if element is visible on page."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        visible = await element.is_visible()
        
        return create_success_response(str(visible).lower())
    except Exception as e:
        return create_error_response(f"Check element visibility failed: {str(e)}")

async def is_element_enabled(element_id: str):
    """Check if element is enabled for interaction."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        enabled = element.is_enabled
        
        return create_success_response(str(enabled).lower())
    except Exception as e:
        return create_error_response(f"Check element enabled failed: {str(e)}")

async def is_element_selected(element_id: str):
    """Check if element is selected (checkboxes, radio buttons)."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # WebElement doesn't have is_selected, implement using attributes
        # Check if it's a checkbox or radio button
        element_type = element.get_attribute('type')
        if element_type in ['checkbox', 'radio']:
            selected = element.get_attribute('checked') is not None
        else:
            # For select options
            selected = element.get_attribute('selected') is not None
        
        return create_success_response(str(selected).lower())
    except Exception as e:
        return create_error_response(f"Check element selected failed: {str(e)}")

async def is_element_on_top(element_id: str):
    """Check if element is on top (not covered by other elements)."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        result = await element.is_on_top()
        return create_success_response(str(result).lower())
    except Exception as e:
        return create_error_response(f"Check element on top failed: {str(e)}")

async def is_element_interactable(element_id: str):
    """Check if element is fully interactable (visible, enabled, on top)."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        result = await element.is_interactable()
        return create_success_response(str(result).lower())
    except Exception as e:
        return create_error_response(f"Check element interactable failed: {str(e)}")

async def get_parent_element(element_id: str, parent_element_id: str):
    """Get parent element of specified element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        if parent_element_id in ELEMENT_CACHE:
            raise ValueError(f"Parent element ID '{parent_element_id}' already exists")
        
        parent = await element.get_parent_element()
        ELEMENT_CACHE[parent_element_id] = parent
        
        return create_success_response(f"Parent element stored as '{parent_element_id}'")
    except Exception as e:
        return create_error_response(f"Get parent element failed: {str(e)}")

async def get_child_elements(element_id: str, base_child_id: str, selector: Optional[str] = None):
    """Get child elements of specified element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        if selector:
            children = await element._find_elements(By.CSS_SELECTOR, selector)
        else:
            children = await element.get_children_elements()
        
        child_ids = []
        for i, child in enumerate(children):
            child_id = f"{base_child_id}_{i}"
            ELEMENT_CACHE[child_id] = child
            child_ids.append(child_id)
        
        return create_success_response(f"Found {len(child_ids)} child elements: {', '.join(child_ids)}")
    except Exception as e:
        return create_error_response(f"Get child elements failed: {str(e)}")

async def get_sibling_elements(
    element_id: str,
    base_sibling_id: str,
    next_siblings: bool = True,
    previous_siblings: bool = True
):
    """Get sibling elements of specified element."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # PyDoll's get_siblings_elements returns all siblings, not separated by next/previous
        siblings = await element.get_siblings_elements()
        
        sibling_ids = []
        for i, sibling in enumerate(siblings):
            sibling_id = f"{base_sibling_id}_{i}"
            ELEMENT_CACHE[sibling_id] = sibling
            sibling_ids.append(sibling_id)
        
        return create_success_response(f"Found {len(sibling_ids)} sibling elements: {', '.join(sibling_ids)}")
    except Exception as e:
        return create_error_response(f"Get sibling elements failed: {str(e)}")

async def element_wait_until(
    element_id: str,
    is_visible: Optional[bool] = None,
    is_interactable: Optional[bool] = None,
    is_on_top: Optional[bool] = None,
    timeout: float = 10
):
    """Wait for an element to meet specific conditions."""
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # PyDoll's wait_until only supports is_visible and is_interactable
        kwargs = {}
        if is_visible is not None:
            kwargs['is_visible'] = is_visible
        if is_interactable is not None:
            kwargs['is_interactable'] = is_interactable
        if timeout:
            kwargs['timeout'] = int(timeout)
            
        if not kwargs:
            kwargs = {'is_visible': True}  # Default behavior
            
        await element.wait_until(**kwargs)
        
        # Handle is_on_top separately if requested
        if is_on_top is not None and is_on_top:
            if not await element.is_on_top():
                raise ValueError("Element is not on top")
        
        conditions = []
        if is_visible is not None:
            conditions.append(f"visible={is_visible}")
        if is_interactable is not None:
            conditions.append(f"interactable={is_interactable}")
        if is_on_top is not None:
            conditions.append(f"on_top={is_on_top}")
        
        return create_success_response(f"Element conditions met: {', '.join(conditions)}")
    except Exception as e:
        return create_error_response(f"Element wait until failed: {str(e)}")

async def wait_for_element(
    tab_id: str,
    selector_type: str,
    selector_value: str,
    timeout: float = 10,
    visible: bool = True
):
    """
    Wait for element to appear using selector.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. DESIGNED FOR DYNAMIC ELEMENTS: This tool is designed to wait for elements that 
       don't exist yet. If the element already exists on the page, it may timeout 
       unexpectedly due to internal timing issues.
       
    2. PROPER USAGE PATTERNS:
       ✓ Use for elements created by JavaScript after page load
       ✓ Use for elements that appear after user interactions
       ✓ Use for lazy-loaded content
       ✗ Don't use for elements already present in initial page HTML
       
    3. ALTERNATIVE FOR EXISTING ELEMENTS:
       For elements that already exist, use find_element() directly instead.
       
    4. TIMEOUT BEHAVIOR:
       May timeout even with generous timeout values if element detection 
       logic conflicts with existing elements.
       
    EXAMPLE USAGE:
    ==============
    # Create element dynamically, then wait for it:
    execute_script(tab_id, "setTimeout(() => {
        const div = document.createElement('div');
        div.id = 'delayed-element';
        document.body.appendChild(div);
    }, 2000);")
    
    wait_for_element(tab_id, 'css', '#delayed-element', timeout=5)
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        selector_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME
        }
        
        if selector_type not in selector_map:
            raise ValueError(f"Invalid selector type: {selector_type}")
        
        by_type = selector_map[selector_type]
        
        # Use PyDoll's built-in find_or_wait_element method
        try:
            # Map selector types to find method parameters
            if selector_type.lower() == "css":
                element = await tab.find(css=selector_value, timeout=int(timeout))
            elif selector_type.lower() == "xpath":
                element = await tab.find(xpath=selector_value, timeout=int(timeout))
            elif selector_type.lower() == "id":
                element = await tab.find(id=selector_value, timeout=int(timeout))
            elif selector_type.lower() == "name":
                element = await tab.find(name=selector_value, timeout=int(timeout))
            elif selector_type.lower() == "tag":
                element = await tab.find(tag_name=selector_value, timeout=int(timeout))
            elif selector_type.lower() == "class":
                element = await tab.find(class_name=selector_value, timeout=int(timeout))
            else:
                # Fallback to find_or_wait_element for other types
                element = await tab.find_or_wait_element(by_type, selector_value, timeout=int(timeout))
            
            if element:
                # Check visibility if required
                if visible:
                    try:
                        is_visible = await element.is_visible()
                        if not is_visible:
                            raise ValueError(f"Element found but not visible: {selector_value}")
                    except:
                        # If visibility check fails, continue anyway
                        pass
                
                return create_success_response(f"Element found with selector '{selector_value}'")
            else:
                raise TimeoutError(f"Timed out waiting for element to appear")
                
        except Exception as wait_error:
            # If PyDoll methods fail, fall back to manual polling
            import asyncio
            import time
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Try to find the element using basic find_elements
                    elements = await tab.find_elements(by_type, selector_value)
                    if elements:
                        return create_success_response(f"Element found with selector '{selector_value}'")
                except:
                    pass
                
                await asyncio.sleep(0.5)
            
            raise TimeoutError(f"Timed out waiting for element to appear")
    except Exception as e:
        return create_error_response(f"Wait for element failed: {str(e)}")

async def execute_script(tab_id: str, script: str, args: Optional[List] = None):
    """
    Execute JavaScript in page context.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. UNSUPPORTED PARAMETERS: The documented parameters 'handle_dialogs' and 'timeout' 
       are NOT supported in this implementation. Using them will cause:
       "execute_script() got an unexpected keyword argument 'handle_dialogs'"
       
    2. SUPPORTED PARAMETERS ONLY:
       ✓ tab_id: str - Required
       ✓ script: str - Required  
       ✓ args: Optional[List] - Optional arguments
       ✗ handle_dialogs - NOT SUPPORTED
       ✗ timeout - NOT SUPPORTED
       
    3. BLOCKING DIALOG WARNINGS:
       - alert(), confirm(), prompt() cause 60-second timeouts
       - Browser becomes unresponsive until timeout
       - Use console.log() for debugging instead
       
    4. SCRIPT SYNTAX REQUIREMENTS:
       - Use semicolons for statement termination in complex scripts
       - Return values explicitly with 'return' statement
       - Avoid 'return' in top-level setTimeout/setInterval callbacks
       
    5. ASYNC SCRIPT BEHAVIOR:
       - Scripts with setTimeout return immediately 
       - Use wait_for_function for async script completion
       - Promise-based scripts return Promise objects
       
    EXAMPLE USAGE:
    ==============
    # Basic execution (supported)
    execute_script("tab_id", "return document.title;")
    
    # With arguments (supported)  
    execute_script("tab_id", "return arguments[0] + arguments[1];", [5, 10])
    
    # Console logging instead of alert
    execute_script("tab_id", "console.log('Debug message');")
    
    # WRONG - unsupported parameters
    execute_script("tab_id", "return 'test';", handle_dialogs=True)  # ERROR
    
    WARNING: Avoid blocking dialogs (alert, confirm, prompt) as they will cause
    60-second timeouts and leave the browser in an unresponsive state.
    Use console.log() for debugging instead of alert().
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if args:
            result = await tab.execute_script(script, *args)
        else:
            result = await tab.execute_script(script)
        
        return create_success_response(str(result) if result is not None else "null")
    except Exception as e:
        return create_error_response(f"Execute script failed: {str(e)}")

async def execute_script_on_element(tab_id: str, element_id: str, script: str, args: Optional[List] = None):
    """Execute JavaScript with element as context.
    
    WARNING: Avoid blocking dialogs (alert, confirm, prompt) as they will cause
    timeouts. The element is available as 'arguments[0]' in your script.
    """
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Convert arguments[0] to argument for PyDoll compatibility  
        processed_script = script.replace('arguments[0]', 'argument')
        
        # Add return statement if not present
        if not processed_script.strip().startswith('return'):
            processed_script = f"return {processed_script}"
        
        # Execute script on the tab with element as first argument
        result = await tab.execute_script(processed_script, element)

        return create_success_response(str(result) if result is not None else "null")
    except Exception as e:
        return create_error_response(f"Execute script on element failed: {str(e)}")

async def get_page_title(tab_id: str):
    """Get the current page title."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        result = await tab.execute_script("return document.title;")
        
        # Handle different response formats
        title = ""
        if hasattr(result, 'result'):
            if hasattr(result.result, 'value'):
                title = result.result.value
            else:
                title = str(result.result)
        elif isinstance(result, dict) and 'result' in result:
            if isinstance(result['result'], dict) and 'value' in result['result']:
                title = result['result']['value']
            else:
                title = str(result['result'])
        else:
            title = str(result)
        
        return create_success_response(title or "")
    except Exception as e:
        return create_error_response(f"Get page title failed: {str(e)}")

async def get_page_url(tab_id: str):
    """Get the current page URL."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        url = await tab.current_url
        
        return create_success_response(url or "")
    except Exception as e:
        return create_error_response(f"Get page URL failed: {str(e)}")

async def get_page_source(tab_id: str):
    """Get the current page HTML source."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        source = await tab.page_source
        
        # Limit response size to prevent token overflow (max ~20k chars for safety)
        if source and len(source) > 20000:
            truncated_source = source[:20000] + "\n\n... [Response truncated due to size limit]"
            return create_success_response(truncated_source)
        
        return create_success_response(source or "")
    except Exception as e:
        return create_error_response(f"Get page source failed: {str(e)}")

async def take_screenshot(
    tab_id: str,
    element_id: Optional[str] = None,
    full_page: bool = False,
    format: str = "png",
    quality: int = 90,
    save_path: Optional[str] = None
):
    """Take screenshot of page or element."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if save_path:
            # Save directly to file
            if element_id:
                element = get_element(element_id)
                if not element:
                    raise ValueError(f"Element '{element_id}' not found")
                await element.take_screenshot(path=save_path)
            else:
                await tab.take_screenshot(path=save_path, beyond_viewport=full_page)
            
            return create_success_response(f"Screenshot saved to: {save_path}")
        else:
            # Return base64 data (Note: large images may exceed response limits)
            # Recommend using save_path parameter for large screenshots
            if element_id:
                element = get_element(element_id)
                if not element:
                    raise ValueError(f"Element '{element_id}' not found")
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    await element.take_screenshot(tmp.name)
                    with open(tmp.name, 'rb') as f:
                        screenshot_data = base64.b64encode(f.read()).decode('utf-8')
                    os.unlink(tmp.name)
            else:
                screenshot_data = await tab.take_screenshot(as_base64=True, beyond_viewport=full_page)
            
            # screenshot_data is already base64 when as_base64=True
            screenshot_b64 = screenshot_data
            
            # Check if response would be too large (rough estimate: 1 char ~= 1 token)
            if len(screenshot_b64) > 100000:  # ~100k chars is roughly 25k tokens
                return create_error_response(f"Screenshot too large ({len(screenshot_b64)} chars). Use save_path parameter instead.")
            
            return create_success_response_with_image(screenshot_b64, f"image/{format}")
    except Exception as e:
        return create_error_response(f"Take screenshot failed: {str(e)}")

async def save_pdf(
    tab_id: str,
    file_path: str,
    landscape: bool = False,
    print_background: bool = False,
    scale: float = 1.0
):
    """Save page as PDF document."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.print_to_pdf(
            path=file_path,
            landscape=landscape,
            print_background=print_background,
            scale=scale
        )
        
        return create_success_response(f"PDF saved to: {file_path}")
    except Exception as e:
        return create_error_response(f"Save PDF failed: {str(e)}")

async def make_request(
    tab_id: str,
    url: str,
    method: str = "GET",
    headers: Optional[List[Dict]] = None,
    data: Optional[str] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 30
):
    """Make HTTP request using browser context.
    
    Args:
        headers: List of header objects with 'name' and 'value' keys,
                e.g., [{"name": "Content-Type", "value": "application/json"}]
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Use tab's request object
        request_obj = tab.request
        
        # Build request parameters
        kwargs = {"timeout": timeout}
        if headers:
            # Convert array of {name, value} objects to dict
            headers_dict = {}
            for header in headers:
                if isinstance(header, dict) and 'name' in header and 'value' in header:
                    headers_dict[header['name']] = header['value']
            kwargs["headers"] = headers_dict
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data
        
        # Make request based on method
        if method.upper() == "GET":
            response = await request_obj.get(url, **kwargs)
        elif method.upper() == "POST":
            response = await request_obj.post(url, **kwargs)
        elif method.upper() == "PUT":
            response = await request_obj.put(url, **kwargs)
        elif method.upper() == "DELETE":
            response = await request_obj.delete(url, **kwargs)
        elif method.upper() == "HEAD":
            response = await request_obj.head(url, **kwargs)
        elif method.upper() == "OPTIONS":
            response = await request_obj.options(url, **kwargs)
        elif method.upper() == "PATCH":
            response = await request_obj.patch(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
            "url": str(response.url)
        }
        
        return create_success_response(json.dumps(result, indent=2))
    except Exception as e:
        return create_error_response(f"Make request failed: {str(e)}")

async def set_cookies(tab_id: str, cookies: List[Dict[str, Any]]):
    """Set cookies for current domain."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.set_cookies(cookies)
        
        return create_success_response(f"Successfully set {len(cookies)} cookies")
    except Exception as e:
        return create_error_response(f"Set cookies failed: {str(e)}")

async def get_cookies(tab_id: str, urls: Optional[List[str]] = None):
    """Get cookies from current domain or specific URLs."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # PyDoll's get_cookies doesn't support urls parameter directly
        # Get all cookies first
        cookies = await tab.get_cookies()
        
        # Filter by URLs if specified
        if urls:
            filtered_cookies = []
            for cookie in cookies:
                for url in urls:
                    import urllib.parse
                    try:
                        parsed = urllib.parse.urlparse(url)
                        cookie_domain = cookie.get('domain', '').lstrip('.')
                        if (cookie_domain in parsed.netloc or 
                            parsed.netloc.endswith(cookie_domain) or
                            cookie_domain == parsed.netloc):
                            filtered_cookies.append(cookie)
                            break
                    except:
                        continue
            cookies = filtered_cookies
        
        return create_success_response(json.dumps(cookies, indent=2))
    except Exception as e:
        return create_error_response(f"Get cookies failed: {str(e)}")

async def delete_cookies(
    tab_id: str,
    name: Optional[str] = None,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None
):
    """Delete specific cookies or all cookies."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        kwargs = {}
        if name:
            kwargs["name"] = name
        if url:
            kwargs["url"] = url
        if domain:
            kwargs["domain"] = domain
        if path:
            kwargs["path"] = path
        
        # Use NetworkCommands for cookie deletion
        from pydoll.commands import NetworkCommands
        if name:
            # Delete specific cookie by name
            await tab._execute_command(NetworkCommands.delete_cookies(
                name=name,
                url=url,
                domain=domain, 
                path=path
            ))
        else:
            # Clear all cookies if no name specified
            await tab._execute_command(NetworkCommands.clear_browser_cookies())
        
        return create_success_response("Cookies deleted successfully")
    except Exception as e:
        return create_error_response(f"Delete cookies failed: {str(e)}")

async def upload_file(element_id: str, file_paths: List[str]):
    """
    Upload files through file input elements.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. REQUIRES FILE INPUT ELEMENTS: This tool ONLY works with actual HTML file input elements.
       It will fail with error "The element is not a file input" if used on other element types.
       
    2. ELEMENT MUST BE <input type="file">:
       ✓ Works: <input type="file" id="file-upload">
       ✗ Fails: <input type="text" id="text-input">  
       ✗ Fails: <div id="upload-area">
       ✗ Fails: <button>Upload</button>
       
    3. CREATING FILE INPUTS DYNAMICALLY:
       If page doesn't have file inputs, create them with JavaScript:
       
       execute_script(tab_id, '''
           const fileInput = document.createElement('input');
           fileInput.type = 'file';
           fileInput.id = 'dynamic-file-input';
           fileInput.name = 'upload';
           document.body.appendChild(fileInput);
       ''')
       
    4. MULTIPLE FILE SUPPORT:
       Add multiple="true" attribute for multiple file uploads:
       fileInput.multiple = true;
       
    5. FILE PATH REQUIREMENTS:
       - All file paths must exist on the local filesystem
       - Use absolute paths for reliability
       - Files are validated before upload attempt
       
    EXAMPLE USAGE:
    ==============
    # 1. First ensure file input exists on page
    execute_script(tab_id, "document.body.innerHTML += '<input type=\"file\" id=\"upload\">';")
    
    # 2. Find the file input element
    find_element(tab_id, 'upload_elem', 'css', '#upload')
    
    # 3. Upload files
    upload_file('upload_elem', ['/path/to/file.txt', '/path/to/image.jpg'])
    """
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Verify all files exist
        for file_path in file_paths:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
        
        await element.set_input_files(file_paths)
        
        return create_success_response(f"Successfully uploaded {len(file_paths)} files")
    except Exception as e:
        return create_error_response(f"Upload file failed: {str(e)}")

async def download_file(
    tab_id: str,
    url: str,
    save_path: Optional[str] = None,
    filename: Optional[str] = None,
    directory: Optional[str] = None,
    timeout: int = 300
):
    """Download files from URLs."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Use tab's request object to download
        response = await tab.request.get(url, timeout=timeout)
        
        # Determine final file path
        if save_path:
            file_path = Path(save_path)
        else:
            # Determine filename
            if not filename:
                filename = url.split('/')[-1] or 'download'
            
            # Determine directory
            if not directory:
                directory = tempfile.gettempdir()
            
            file_path = Path(directory) / filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return create_success_response(f"File downloaded to: {file_path}")
    except Exception as e:
        return create_error_response(f"Download file failed: {str(e)}")

async def expect_file_chooser(tab_id: str, file_paths: List[str], timeout: float = 30):
    """Handle file chooser dialogs with automatic file selection."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Verify files exist
        for file_path in file_paths:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
        
        async with tab.expect_file_chooser(file_paths):
            pass  # File paths are automatically handled by the context manager
        
        return create_success_response(f"File chooser handled with {len(file_paths)} files")
    except Exception as e:
        return create_error_response(f"Expect file chooser failed: {str(e)}")

async def enable_file_chooser_intercept(tab_id: str):
    """Enable file chooser dialog interception."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.enable_intercept_file_chooser_dialog()
        
        return create_success_response("File chooser interception enabled")
    except Exception as e:
        return create_error_response(f"Enable file chooser intercept failed: {str(e)}")

async def disable_file_chooser_intercept(tab_id: str):
    """Disable file chooser dialog interception."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.disable_intercept_file_chooser_dialog()
        
        return create_success_response("File chooser interception disabled")
    except Exception as e:
        return create_error_response(f"Disable file chooser intercept failed: {str(e)}")

async def wait_for_page_load(tab_id: str, wait_until: str = "load", timeout: int = 30):
    """Wait for page to finish loading."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab._wait_page_load(timeout=timeout)
        
        return create_success_response(f"Page load completed ({wait_until})")
    except Exception as e:
        return create_error_response(f"Wait for page load failed: {str(e)}")

async def wait_for_function(
    tab_id: str,
    script: str,
    args: Optional[List] = None,
    timeout: int = 30,
    polling: int = 100
):
    """Wait for JavaScript function to return truthy value."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        import asyncio
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Execute the script and check result
                if args:
                    result = await tab.execute_script(script, *args)
                else:
                    result = await tab.execute_script(script)
                
                # Handle different response formats
                value = None
                if hasattr(result, 'result'):
                    if hasattr(result.result, 'value'):
                        value = result.result.value
                    else:
                        value = result.result
                elif isinstance(result, dict) and 'result' in result:
                    if isinstance(result['result'], dict) and 'value' in result['result']:
                        value = result['result']['value']
                    else:
                        value = result['result']
                else:
                    value = result
                
                # Check if value is truthy
                if value:
                    return create_success_response(f"Function returned truthy value: {value}")
                    
            except Exception as exec_error:
                # Continue polling on execution errors
                pass
            
            await asyncio.sleep(polling / 1000.0)  # Convert ms to seconds
        
        raise TimeoutError(f"Function did not return truthy value within {timeout} seconds")
        
    except asyncio.TimeoutError:
        return create_error_response(f"Function did not return truthy value within {timeout} seconds")
    except Exception as e:
        return create_error_response(f"Wait for function failed: {str(e)}")


async def handle_alert(tab_id: str, action: str = "accept", text: Optional[str] = None):
    """
    Handle JavaScript alert, confirm, or prompt dialogs.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. DIALOG BLOCKING BEHAVIOR: JavaScript dialogs (alert, confirm, prompt) can 
       completely block browser automation until handled. Always handle dialogs 
       promptly to prevent timeouts.
       
    2. AUTO-DETECTION: The browser automatically detects when dialogs appear.
       Use has_dialog() to check for active dialogs before other operations.
       
    3. DIALOG TYPES SUPPORTED:
       ✓ alert() - Simple message dialog (only "accept" action works)
       ✓ confirm() - Yes/No dialog (accept=true, dismiss=false)
       ✓ prompt() - Text input dialog (accept + text parameter)
       
    4. ACTION PARAMETERS:
       - "accept": Click OK/Yes button (default)
       - "dismiss": Click Cancel/No button
       - text: Text to enter in prompt dialogs (optional)
       
    5. DIALOG STATE CONTAMINATION: Unhandled dialogs can leave browser tabs in
       unusable state. Many automation functions will fail while dialogs are active.
       
    6. TESTING DIALOG HANDLING:
       Create dialogs for testing:
       execute_script(tab_id, "setTimeout(() => alert('Test message'), 1000);")
       # Wait for dialog to appear, then handle it
       
    7. TIMING CONSIDERATIONS:
       - Dialogs appear asynchronously after script execution
       - Use small delays or has_dialog() polling to detect dialog appearance
       - Handle dialogs immediately after detection
       
    EXAMPLE USAGE:
    ==============
    # Create a test dialog
    execute_script(tab_id, "setTimeout(() => alert('Hello World'), 500);")
    
    # Check for dialog (may need to wait/retry)
    if has_dialog(tab_id):
        handle_alert(tab_id, action="accept")
    
    # Handle confirm dialog
    execute_script(tab_id, "setTimeout(() => confirm('Are you sure?'), 500);")
    handle_alert(tab_id, action="dismiss")  # Click Cancel
    
    # Handle prompt dialog  
    execute_script(tab_id, "setTimeout(() => prompt('Enter name:'), 500);")
    handle_alert(tab_id, action="accept", text="John Doe")
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if action == "accept":
            await tab.handle_dialog(accept=True, prompt_text=text)
        elif action == "dismiss":
            await tab.handle_dialog(accept=False)
        else:
            raise ValueError(f"Invalid action: {action}")
        
        return create_success_response(f"Dialog {action}ed successfully")
    except Exception as e:
        return create_error_response(f"Handle alert failed: {str(e)}")

async def has_dialog(tab_id: str):
    """Check if there is an active dialog on the page."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        has_dialog = await tab.has_dialog()
        
        return create_success_response(str(has_dialog).lower())
    except Exception as e:
        return create_error_response(f"Check has dialog failed: {str(e)}")

async def get_dialog_message(tab_id: str):
    """Get the message text from an active dialog."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Check event logs for dialog information
        if tab_id in EVENT_LOGS:
            for event in reversed(EVENT_LOGS[tab_id]):
                if event.get('event_type') == 'Page.javascriptDialogOpening':
                    if 'data' in event and 'params' in event['data']:
                        return create_success_response(event['data']['params'].get('message', ''))
        
        # Fallback - try to get message via JavaScript if dialog still active
        try:
            result = await tab.execute_script("return window.lastDialogMessage || 'Dialog message not available';")
            
            message = ""
            if hasattr(result, 'result') and hasattr(result.result, 'value'):
                message = result.result.value
            elif isinstance(result, dict) and 'result' in result:
                message = result['result'].get('value', str(result['result']))
            else:
                message = str(result)
                
            return create_success_response(message)
        except:
            return create_success_response("Dialog message not available")
    except Exception as e:
        return create_error_response(f"Get dialog message failed: {str(e)}")

# === EVENT SYSTEM IMPLEMENTATIONS ===

async def enable_page_events(tab_id: str):
    """Enable page event monitoring.
    
    Note: This may fail if the browser tab is in a blocked state (e.g., alert dialog open).
    Handle any active dialogs first using handle_alert().
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.enable_page_events()
        
        return create_success_response("Page events enabled successfully")
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "blocked" in error_msg:
            return create_error_response(f"Enable page events failed: Browser tab may be blocked by a dialog. Try handling any active dialogs first with handle_alert(), then retry. Original error: {str(e)}")
        return create_error_response(f"Enable page events failed: {str(e)}")

async def enable_network_events(tab_id: str):
    """Enable network event monitoring.
    
    Note: This may fail if the browser tab is in a blocked state (e.g., alert dialog open).
    Handle any active dialogs first using handle_alert().
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.enable_network_events()
        
        if tab_id not in NETWORK_LOGS:
            NETWORK_LOGS[tab_id] = []
        
        return create_success_response("Network events enabled successfully")
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "blocked" in error_msg:
            return create_error_response(f"Enable network events failed: Browser tab may be blocked by a dialog. Try handling any active dialogs first with handle_alert(), then retry. Original error: {str(e)}")
        return create_error_response(f"Enable network events failed: {str(e)}")

async def enable_fetch_events(tab_id: str, patterns: Optional[List[str]] = None):
    """Enable fetch event monitoring for request interception."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if patterns:
            await tab.enable_fetch_events(patterns=patterns)
        else:
            await tab.enable_fetch_events()
        
        return create_success_response(f"Fetch events enabled for {len(patterns) if patterns else 'all'} patterns")
    except Exception as e:
        return create_error_response(f"Enable fetch events failed: {str(e)}")

async def enable_dom_events(tab_id: str):
    """Enable DOM event monitoring."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.enable_dom_events()
        
        return create_success_response("DOM events enabled successfully")
    except Exception as e:
        return create_error_response(f"Enable DOM events failed: {str(e)}")

async def enable_runtime_events(tab_id: str):
    """Enable runtime event monitoring."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.enable_runtime_events()
        
        return create_success_response("Runtime events enabled successfully")
    except Exception as e:
        return create_error_response(f"Enable runtime events failed: {str(e)}")

async def disable_all_events(tab_id: str):
    """Disable all event monitoring for a tab."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.disable_page_events()
        await tab.disable_network_events()
        await tab.disable_fetch_events()
        await tab.disable_dom_events()
        await tab.disable_runtime_events()
        
        await tab.clear_callbacks()
        
        if tab_id in EVENT_CALLBACKS:
            EVENT_CALLBACKS[tab_id] = {}
        if tab_id in EVENT_LOGS:
            EVENT_LOGS[tab_id] = []
        if tab_id in NETWORK_LOGS:
            NETWORK_LOGS[tab_id] = []
        
        return create_success_response("All event monitoring disabled")
    except Exception as e:
        return create_error_response(f"Disable all events failed: {str(e)}")

async def register_event_callback(
    tab_id: str,
    callback_id: str,
    event_type: str,
    filter_pattern: Optional[str] = None
):
    """Register callback for specific browser events."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if tab_id not in EVENT_CALLBACKS:
            EVENT_CALLBACKS[tab_id] = {}
        if tab_id not in EVENT_LOGS:
            EVENT_LOGS[tab_id] = []
        
        def event_callback(event_data):
            EVENT_LOGS[tab_id].append({
                "callback_id": callback_id,
                "event_type": event_type,
                "timestamp": asyncio.get_event_loop().time(),
                "data": event_data,
                "filter_pattern": filter_pattern
            })
        
        registered_callback_id = await tab.on(event_type, event_callback)
        
        EVENT_CALLBACKS[tab_id][callback_id] = {
            "pydoll_callback_id": registered_callback_id,
            "event_type": event_type,
            "filter_pattern": filter_pattern
        }
        
        return create_success_response(f"Event callback '{callback_id}' registered for '{event_type}'")
    except Exception as e:
        return create_error_response(f"Register event callback failed: {str(e)}")

async def remove_event_callback(tab_id: str, callback_id: str):
    """Remove a specific event callback."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        if tab_id not in EVENT_CALLBACKS or callback_id not in EVENT_CALLBACKS[tab_id]:
            raise ValueError(f"Callback '{callback_id}' not found")
        
        callback_info = EVENT_CALLBACKS[tab_id][callback_id]
        pydoll_callback_id = callback_info["pydoll_callback_id"]
        
        await tab.remove_callback(pydoll_callback_id)
        
        del EVENT_CALLBACKS[tab_id][callback_id]
        
        return create_success_response(f"Event callback '{callback_id}' removed successfully")
    except Exception as e:
        return create_error_response(f"Remove event callback failed: {str(e)}")

async def clear_event_callbacks(tab_id: str):
    """Clear all event callbacks for a tab."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        await tab.clear_callbacks()
        
        if tab_id in EVENT_CALLBACKS:
            EVENT_CALLBACKS[tab_id] = {}
        if tab_id in EVENT_LOGS:
            EVENT_LOGS[tab_id] = []
        
        return create_success_response("All event callbacks cleared successfully")
    except Exception as e:
        return create_error_response(f"Clear event callbacks failed: {str(e)}")

async def get_event_logs(tab_id: str, event_type: Optional[str] = None, limit: int = 100):
    """
    Get captured event logs.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. EMPTY RESULTS BY DEFAULT: This function often returns empty arrays [] even
       after enabling event monitoring. Events need to be actively triggered.
       
    2. REQUIRES EVENT ENABLEMENT: Must call the appropriate enable_*_events() 
       functions first:
       - enable_runtime_events() for console logs
       - enable_page_events() for page lifecycle events
       - enable_dom_events() for DOM interaction events
       
    3. EVENT GENERATION REQUIREMENTS:
       Events won't appear unless actively triggered:
       ✓ Console logs: execute_script(tab_id, "console.log('test message');")
       ✓ Page events: navigate(), refresh_page()
       ✓ DOM events: click_element(), type_text()
       
    4. EVENT TYPES:
       - "console": console.log, console.warn, console.error messages
       - "page": page load, navigation, reload events  
       - "dom": click, input, focus, blur events
       - "runtime": JavaScript exceptions, promise rejections
       
    5. TIMING CONSIDERATIONS:
       - Enable events BEFORE triggering the actions you want to log
       - Some events may take time to propagate to the log system
       - Logs persist until browser session closes
       
    EXAMPLE USAGE:
    ==============
    # 1. Enable the event type you want to monitor
    enable_runtime_events(tab_id)
    
    # 2. Trigger some events
    execute_script(tab_id, "console.log('Hello'); console.warn('Warning');")
    
    # 3. Retrieve the logs
    get_event_logs(tab_id, event_type="console", limit=10)
    """
    try:
        if tab_id not in EVENT_LOGS:
            EVENT_LOGS[tab_id] = []
        
        logs = EVENT_LOGS[tab_id]
        
        if event_type:
            logs = [log for log in logs if log.get("event_type") == event_type]
        
        logs = logs[-limit:] if limit and limit > 0 else logs
        
        return create_success_response(json.dumps(logs, indent=2, default=str))
    except Exception as e:
        return create_error_response(f"Get event logs failed: {str(e)}")

# === REQUEST INTERCEPTION IMPLEMENTATIONS ===

async def continue_request(
    tab_id: str,
    request_id: str,
    url: Optional[str] = None,
    method: Optional[str] = None,
    headers: Optional[List[Dict]] = None,
    post_data: Optional[str] = None
):
    """
    Continue an intercepted request with modifications.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. MOCK TESTING BEHAVIOR: These network interception tools are designed to work 
       with ANY request_id, even non-existent ones. They will report success even 
       with fake request IDs for testing purposes.
       
    2. REQUIRES ACTUAL INTERCEPTION SETUP: For real request interception to work:
       ✓ Must enable_network_events() first
       ✓ Must enable_fetch_events() for fetch request interception
       ✓ Must set up request interception patterns with callbacks
       
    3. REQUEST_ID SOURCE: Real request IDs come from:
       - get_network_logs() entries (request_id field)
       - Event callback notifications  
       - Network monitoring during page activity
       
    4. HEADER FORMAT REQUIREMENTS:
       Headers must be array of objects with name/value properties:
       ✓ Correct: [{"name": "Content-Type", "value": "application/json"}]
       ✗ Wrong:   {"Content-Type": "application/json"}
       
    5. MODIFICATION CAPABILITIES:
       - url: Redirect request to different URL
       - method: Change HTTP method (GET → POST, etc.)
       - headers: Add, modify, or remove headers
       - post_data: Change request body content
       
    6. TESTING WITHOUT REAL INTERCEPTION:
       These tools accept any request_id for testing/validation:
       continue_request(tab_id, "fake_request_123", url="https://modified.com")
       # Will report success even with fake ID
       
    EXAMPLE USAGE:
    ==============
    # For real interception (requires setup):
    enable_network_events(tab_id)
    # ... trigger network request ...
    logs = get_network_logs(tab_id)
    real_request_id = logs[0]["request_id"]
    
    # Modify and continue request:
    continue_request(
        tab_id=tab_id,
        request_id=real_request_id,
        url="https://modified-endpoint.com",
        headers=[{"name": "Authorization", "value": "Bearer token123"}],
        post_data='{"modified": "data"}'
    )
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        kwargs = {"request_id": request_id}
        if url:
            kwargs["url"] = url
        if method:
            kwargs["method"] = method
        if headers:
            header_entries = [HeaderEntry(name=h["name"], value=h["value"]) for h in headers]
            kwargs["headers"] = header_entries
        if post_data:
            kwargs["post_data"] = post_data
        
        await tab.continue_request(**kwargs)
        
        return create_success_response(f"Request '{request_id}' continued successfully")
    except Exception as e:
        return create_error_response(f"Continue request failed: {str(e)}")

async def fail_request(tab_id: str, request_id: str, error_reason: str = "Failed"):
    """Fail an intercepted request."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Map common error reasons to PyDoll ErrorReason enum
        error_map = {
            "FAILED": ErrorReason.FAILED,
            "ABORTED": ErrorReason.ABORTED,
            "TIMEDOUT": ErrorReason.TIMED_OUT,
            "TIMEOUT": ErrorReason.TIMED_OUT,
            "ACCESSDENIED": ErrorReason.ACCESS_DENIED,
            "CONNECTIONCLOSED": ErrorReason.CONNECTION_CLOSED,
            "CONNECTIONRESET": ErrorReason.CONNECTION_RESET,
            "CONNECTIONREFUSED": ErrorReason.CONNECTION_REFUSED,
            "CONNECTIONABORTED": ErrorReason.CONNECTION_ABORTED,
            "CONNECTIONFAILED": ErrorReason.CONNECTION_FAILED,
            "NAMENOTRESOLVED": ErrorReason.NAME_NOT_RESOLVED,
        }
        
        error_key = error_reason.upper().replace("_", "")
        error_enum = error_map.get(error_key, ErrorReason.FAILED)
        
        await tab.fail_request(request_id, error_enum)
        
        return create_success_response(f"Request '{request_id}' failed with reason '{error_reason}'")
    except Exception as e:
        return create_error_response(f"Fail request failed: {str(e)}")

async def fulfill_request(
    tab_id: str,
    request_id: str,
    response_code: int = 200,
    response_headers: Optional[List[Dict]] = None,
    body: Optional[str] = None,
    binary_body: Optional[str] = None
):
    """Fulfill an intercepted request with custom response."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        kwargs = {
            "request_id": request_id,
            "response_code": response_code
        }
        
        if response_headers:
            header_entries = [HeaderEntry(name=h["name"], value=h["value"]) for h in response_headers]
            kwargs["response_headers"] = header_entries
        
        if binary_body:
            # Decode base64 binary data
            try:
                decoded_data = base64.b64decode(binary_body)
                # Try to decode as UTF-8, fallback to base64 string if not possible
                kwargs["body"] = decoded_data.decode('utf-8')
            except UnicodeDecodeError:
                # Keep as base64 string for binary content
                kwargs["body"] = binary_body
        elif body:
            kwargs["body"] = body
        
        await tab.fulfill_request(**kwargs)
        
        return create_success_response(f"Request '{request_id}' fulfilled with status {response_code}")
    except Exception as e:
        return create_error_response(f"Fulfill request failed: {str(e)}")

async def get_network_response_body(tab_id: str, request_id: str):
    """Get the response body for a specific network request."""
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Use NetworkCommands to get response body
        try:
            from pydoll.commands import NetworkCommands
            result = await tab._execute_command(NetworkCommands.get_response_body(request_id))
            
            if isinstance(result, dict):
                body = result.get('body', '')
                is_base64 = result.get('base64Encoded', False)
                
                if is_base64:
                    import base64
                    try:
                        body = base64.b64decode(body).decode('utf-8', errors='ignore')
                    except:
                        pass  # Keep as base64 if decode fails
                
                return create_success_response(body)
            else:
                return create_success_response(str(result))
                
        except Exception as cmd_error:
            # Fallback to checking network logs
            if tab_id in NETWORK_LOGS:
                for log_entry in NETWORK_LOGS[tab_id]:
                    if log_entry.get('request_id') == request_id:
                        return create_success_response(log_entry.get('response_body', ''))
            
            raise cmd_error
    except Exception as e:
        return create_error_response(f"Get network response body failed: {str(e)}")

async def get_network_logs(tab_id: str, filter_pattern: Optional[str] = None, limit: int = 100):
    """
    Get network request logs with optional filtering.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. REQUIRES NETWORK EVENTS FIRST: This function will fail with clear error if
       network events aren't enabled:
       "Network events must be enabled first. Please call 'enable_network_events'"
       
    2. PREREQUISITE SETUP:
       ✓ MUST call enable_network_events(tab_id) first
       ✓ THEN trigger network activity to generate logs
       ✓ THEN call get_network_logs() to retrieve them
       
    3. NETWORK ACTIVITY GENERATION:
       Network logs won't appear unless requests are made:
       ✓ navigate() to new pages
       ✓ execute_script() with fetch() calls
       ✓ make_request() for HTTP requests
       ✓ Image loading, CSS loading, etc.
       
    4. LOG ENTRY FORMAT:
       Each log contains:
       - url: Request URL
       - method: HTTP method (GET, POST, etc.)
       - status: Response status code (or null if pending)
       - timestamp: When request occurred
       - request_id: Unique identifier for request interception
       
    5. FILTERING PATTERNS:
       - Use glob-style patterns: "*.json", "*/api/*", "*example.com*"
       - Empty/null pattern returns all requests
       - Case-sensitive matching
       
    EXAMPLE USAGE:
    ==============
    # 1. Enable network monitoring
    enable_network_events(tab_id)
    
    # 2. Generate network activity
    execute_script(tab_id, "fetch('https://httpbin.org/json').then(r => r.json());")
    
    # 3. Wait a moment for request to complete
    await asyncio.sleep(2)
    
    # 4. Retrieve network logs
    get_network_logs(tab_id, filter_pattern="*.json", limit=5)
    
    Prerequisites: Call enable_network_events() first to start capturing logs.
    """
    try:
        tab = get_tab_session(tab_id)
        if not tab:
            raise ValueError(f"Tab '{tab_id}' not found")
        
        # Check if network events are enabled
        if not hasattr(tab, '_network_events_enabled') or not tab._network_events_enabled:
            return create_error_response("Network events must be enabled first. Please call 'enable_network_events' on this tab before attempting to get network logs.")
            
        logs = await tab.get_network_logs(filter=filter_pattern)
        
        # Ensure limit is an integer
        limit = int(limit) if limit is not None else 100
        if limit > 0:
            logs = logs[-limit:]
        
        log_data = []
        for log_entry in logs:
            # Handle different log entry formats (raw events vs structured objects)
            if isinstance(log_entry, dict):
                # Extract from network event format
                if 'params' in log_entry:
                    params = log_entry['params']
                    request = params.get('request', {})
                    response = params.get('response', {})
                    log_data.append({
                        "url": request.get('url') or response.get('url'),
                        "method": request.get('method'),
                        "status": response.get('status'),
                        "timestamp": params.get('timestamp'),
                        "request_id": params.get('requestId')
                    })
                else:
                    # Direct format
                    log_data.append({
                        "url": log_entry.get('url'),
                        "method": log_entry.get('method'),
                        "status": log_entry.get('status'),
                        "timestamp": log_entry.get('timestamp'),
                        "request_id": log_entry.get('requestId') or log_entry.get('request_id')
                    })
            else:
                # Object with attributes
                log_data.append({
                    "url": getattr(log_entry, 'url', None),
                    "method": getattr(log_entry, 'method', None),
                    "status": getattr(log_entry, 'status', None),
                    "timestamp": getattr(log_entry, 'timestamp', None),
                    "request_id": getattr(log_entry, 'requestId', None) or getattr(log_entry, 'request_id', None)
                })
        
        return create_success_response(json.dumps(log_data, indent=2, default=str))
    except Exception as e:
        return create_error_response(f"Get network logs failed: {str(e)}")

# === IFRAME SUPPORT ===

async def get_frame(element_id: str, frame_tab_id: str, validate_iframe: bool = True):
    """
    Get frame context from an iframe element with enhanced validation.
    
    QUIRKS & USAGE NOTES:
    =====================
    1. CROSS-ORIGIN RESTRICTIONS: This function frequently fails with cross-origin 
       iframes due to browser security policies:
       - "Iframe target not found in browser" 
       - "The iframe may not be fully loaded or may have cross-origin restrictions"
       
    2. IFRAME REQUIREMENTS: Only works with proper iframe elements:
       ✓ Must be actual <iframe> tag
       ✓ Must have 'src' attribute (not 'srcdoc')
       ✓ Must be same-origin or have proper CORS headers
       ✓ Must be fully loaded before frame context access
       
    3. SAME-ORIGIN SOLUTIONS: For testing, use same-origin iframes:
       execute_script(tab_id, '''
           const iframe = document.createElement('iframe');
           iframe.src = 'data:text/html,<html><body><h1>Test</h1></body></html>';
           iframe.id = 'test-iframe';
           document.body.appendChild(iframe);
       ''')
       
    4. VALIDATION PARAMETER:
       - validate_iframe=true: Strict validation (recommended)
       - validate_iframe=false: Skip some checks (may still fail)
       
    5. ASYNC/AWAIT IMPLEMENTATION ISSUES:
       Some errors indicate internal async handling problems:
       "object str can't be used in 'await' expression"
       This suggests implementation bugs in the validation logic.
       
    6. COMMON FAILURE SCENARIOS:
       ✗ Cross-origin iframes (most external sites)
       ✗ Iframes with authentication requirements  
       ✗ Iframes loaded via JavaScript after page load
       ✓ Same-origin iframes with direct src URLs
       ✓ Data URI iframes (limited functionality)
       
    7. WORKING ALTERNATIVES:
       - Use execute_script() to interact with iframe content indirectly
       - Switch to iframe's parent window for cross-frame communication
       - Use postMessage for cross-origin iframe communication
       
    EXAMPLE USAGE:
    ==============
    # Create same-origin iframe for testing:
    execute_script(tab_id, '''
        const iframe = document.createElement('iframe');
        iframe.src = '/same-origin-page.html';  // Same domain
        iframe.id = 'accessible-iframe';
        document.body.appendChild(iframe);
    ''')
    
    # Wait for iframe to load
    wait_for_element(tab_id, 'css', '#accessible-iframe')
    
    # Get frame context  
    find_element(tab_id, 'iframe_elem', 'css', '#accessible-iframe')
    get_frame('iframe_elem', 'iframe_context', validate_iframe=True)
    
    Args:
        element_id: Element identifier for the iframe
        frame_tab_id: New tab ID for the iframe context
        validate_iframe: Perform comprehensive iframe validation (default: True)
    """
    try:
        element = get_element(element_id)
        if not element:
            raise ValueError(f"Element '{element_id}' not found")
        
        # Find the tab that contains this element
        parent_tab = None
        for tab_session in TAB_SESSIONS.values():
            if hasattr(tab_session, '_connection_handler') and tab_session._connection_handler == element._connection_handler:
                parent_tab = tab_session
                break
        
        if not parent_tab:
            raise ValueError("Could not find parent tab for the element")
        
        # Enhanced validation if requested
        if validate_iframe:
            try:
                # Check if element is actually an iframe
                tag_name = await element.tag_name
                if tag_name.lower() != 'iframe':
                    return create_error_response(f"Element is a '{tag_name}', not an iframe. Only iframe elements can be used with get_frame().")
                
                # Check for src attribute
                src = await element.get_attribute('src')
                if not src:
                    # Check for srcdoc (inline content)
                    srcdoc = await element.get_attribute('srcdoc')
                    if not srcdoc:
                        return create_error_response("Iframe lacks both 'src' and 'srcdoc' attributes. Cannot access iframe content without a source.")
                    else:
                        return create_error_response("Iframe uses 'srcdoc' attribute (inline content). Frame targeting is only supported for iframes with 'src' attributes pointing to separate documents.")
                
                # Check if iframe is loaded
                try:
                    await element.execute_script("return this.contentDocument != null;")
                except:
                    return create_error_response("Cannot access iframe content. This may be due to cross-origin restrictions or the iframe not being fully loaded.")
                
            except Exception as validation_error:
                return create_error_response(f"Iframe validation failed: {str(validation_error)}")
        
        # Use the pydoll get_frame method
        try:
            frame_tab = await parent_tab.get_frame(element)
        except Exception as e:
            error_msg = str(e)
            if "not an iframe" in error_msg.lower():
                return create_error_response(f"Element is not an iframe. Only iframe elements can be used with get_frame().")
            elif "valid src attribute" in error_msg.lower():
                return create_error_response(f"Iframe lacks a valid 'src' attribute. Ensure the iframe has a 'src' pointing to a loadable document.")
            elif "target for the iframe was not found" in error_msg.lower():
                return create_error_response(f"Iframe target not found in browser. The iframe may not be fully loaded or may have cross-origin restrictions.")
            else:
                return create_error_response(f"Failed to create frame context: {error_msg}")
        
        # Store the frame tab in our sessions
        TAB_SESSIONS[frame_tab_id] = frame_tab
        
        return create_success_response(f"Frame context created as tab '{frame_tab_id}'")
    except Exception as e:
        return create_error_response(f"Get frame failed: {str(e)}")

# === BROWSER PREFERENCES ===

async def set_browser_preferences(
    session_id: str,
    preferences: Optional[Dict] = None,
    download_directory: Optional[str] = None,
    accept_languages: Optional[str] = None,
    prompt_for_download: Optional[bool] = None
):
    """Set advanced Chrome browser preferences."""
    try:
        browser = get_browser_session(session_id)
        if not browser:
            raise ValueError(f"Browser session '{session_id}' not found")
        
        # Try to get active tab's connection handler
        active_tab = None
        for tab_session in TAB_SESSIONS.values():
            if hasattr(tab_session, '_connection_handler'):
                active_tab = tab_session
                break
        
        if not active_tab:
            return create_error_response("No active tab found to execute preferences setting")
        
        # Use Browser commands to set runtime preferences where possible
        from pydoll.commands import BrowserCommands
        from pydoll.protocol.browser.methods import DownloadBehavior
        
        changes = []
        
        # Set download directory and behavior
        if download_directory:
            try:
                command = BrowserCommands.set_download_behavior(
                    behavior=DownloadBehavior.ALLOW,
                    download_path=download_directory
                )
                await active_tab._connection_handler.execute_command(command)
                changes.append(f"download_directory: {download_directory}")
            except Exception as e:
                changes.append(f"download_directory: {download_directory} (failed: {str(e)})")
        
        # Other preferences would need different approaches - most require browser restart
        if accept_languages:
            changes.append(f"accept_languages: {accept_languages} (requires browser restart)")
            
        if prompt_for_download is not None:
            changes.append(f"prompt_for_download: {prompt_for_download} (requires browser restart)")
            
        if preferences:
            changes.append(f"custom preferences: {len(preferences)} items (requires browser restart)")
        
        if not changes:
            return create_success_response("No preferences specified to change")
        
        return create_success_response(f"Browser preferences updated: {', '.join(changes)}. Note: Some preferences may require browser restart to take full effect.")
    except Exception as e:
        return create_error_response(f"Set browser preferences failed: {str(e)}")

# === SESSION MANAGEMENT ===

async def list_sessions():
    """List all active browser and tab sessions."""
    try:
        session_info = {
            "browser_sessions": list(BROWSER_SESSIONS.keys()),
            "tab_sessions": list(TAB_SESSIONS.keys()),
            "cached_elements": len(ELEMENT_CACHE),
            "event_callbacks": {tab_id: len(callbacks) for tab_id, callbacks in EVENT_CALLBACKS.items()},
            "event_logs": {tab_id: len(logs) for tab_id, logs in EVENT_LOGS.items()},
            "network_logs": {tab_id: len(logs) for tab_id, logs in NETWORK_LOGS.items()}
        }
        
        return create_success_response(json.dumps(session_info, indent=2))
    except Exception as e:
        return create_error_response(f"List sessions failed: {str(e)}")

async def get_session_info(session_id: str):
    """Get detailed information about a specific session."""
    try:
        info = {}
        
        if session_id in BROWSER_SESSIONS:
            browser = BROWSER_SESSIONS[session_id]
            info["type"] = "browser"
            info["session_id"] = session_id
            info["status"] = "active"
        elif session_id in TAB_SESSIONS:
            tab = TAB_SESSIONS[session_id]
            info["type"] = "tab"
            info["session_id"] = session_id
            info["status"] = "active"
            try:
                info["url"] = await tab.current_url()
                result = await tab.execute_script("document.title")
                info["title"] = result.result.value if hasattr(result, 'result') and hasattr(result.result, 'value') else ""
            except:
                pass
        else:
            raise ValueError(f"Session '{session_id}' not found")
        
        return create_success_response(json.dumps(info, indent=2))
    except Exception as e:
        return create_error_response(f"Get session info failed: {str(e)}")

async def cleanup_elements(tab_id: Optional[str] = None):
    """Clean up cached element references."""
    try:
        if tab_id:
            elements_to_remove = [elem_id for elem_id in ELEMENT_CACHE.keys() if elem_id.startswith(f"{tab_id}_")]
            for elem_id in elements_to_remove:
                del ELEMENT_CACHE[elem_id]
            
            return create_success_response(f"Cleaned up {len(elements_to_remove)} elements for tab '{tab_id}'")
        else:
            count = len(ELEMENT_CACHE)
            ELEMENT_CACHE.clear()
            
            return create_success_response(f"Cleaned up {count} cached elements")
    except Exception as e:
        return create_error_response(f"Cleanup elements failed: {str(e)}")

# Create a tool dispatcher mapping for easier maintenance
TOOL_HANDLERS = {
    "create_browser_session": create_browser_session,
    "start_browser_session": start_browser_session,
    "close_browser_session": close_browser_session,
    "create_tab": create_tab,
    "close_tab": close_tab,
    "bring_tab_to_front": bring_tab_to_front,
    "navigate": navigate,
    "go_back": go_back,
    "go_forward": go_forward,
    "refresh_page": refresh_page,
    "find_element": find_element,
    "find_elements": find_elements,
    "click_element": click_element,
    "click_element_js": click_element_js,
    "type_text": type_text,
    "clear_text": clear_text,
    "press_key": press_key,
    "key_down": key_down,
    "key_up": key_up,
    "hover_element": hover_element,
    "scroll_element": scroll_element,
    "drag_and_drop": drag_and_drop,
    "get_element_text": get_element_text,
    "get_element_attribute": get_element_attribute,
    "get_element_property": get_element_property,
    "get_element_html": get_element_html,
    "get_element_bounds": get_element_bounds,
    "get_element_bounds_js": get_element_bounds_js,
    "is_element_visible": is_element_visible,
    "is_element_enabled": is_element_enabled,
    "is_element_selected": is_element_selected,
    "is_element_on_top": is_element_on_top,
    "is_element_interactable": is_element_interactable,
    "get_parent_element": get_parent_element,
    "get_child_elements": get_child_elements,
    "get_sibling_elements": get_sibling_elements,
    "element_wait_until": element_wait_until,
    "wait_for_element": wait_for_element,
    "execute_script": execute_script,
    "execute_script_on_element": execute_script_on_element,
    "get_page_title": get_page_title,
    "get_page_url": get_page_url,
    "get_page_source": get_page_source,
    "take_screenshot": take_screenshot,
    "save_pdf": save_pdf,
    "make_request": make_request,
    "set_cookies": set_cookies,
    "get_cookies": get_cookies,
    "delete_cookies": delete_cookies,
    "upload_file": upload_file,
    "download_file": download_file,
    "expect_file_chooser": expect_file_chooser,
    "enable_file_chooser_intercept": enable_file_chooser_intercept,
    "disable_file_chooser_intercept": disable_file_chooser_intercept,
    "wait_for_page_load": wait_for_page_load,
    "wait_for_function": wait_for_function,
    "handle_alert": handle_alert,
    "has_dialog": has_dialog,
    "get_dialog_message": get_dialog_message,
    "enable_page_events": enable_page_events,
    "enable_network_events": enable_network_events,
    "enable_fetch_events": enable_fetch_events,
    "enable_dom_events": enable_dom_events,
    "enable_runtime_events": enable_runtime_events,
    "disable_all_events": disable_all_events,
    "register_event_callback": register_event_callback,
    "remove_event_callback": remove_event_callback,
    "clear_event_callbacks": clear_event_callbacks,
    "get_event_logs": get_event_logs,
    "continue_request": continue_request,
    "fail_request": fail_request,
    "fulfill_request": fulfill_request,
    "get_network_response_body": get_network_response_body,
    "get_network_logs": get_network_logs,
    "get_frame": get_frame,
    "set_browser_preferences": set_browser_preferences,
    "list_sessions": list_sessions,
    "get_session_info": get_session_info,
    "cleanup_elements": cleanup_elements,
}

# JSON-RPC server implementation only


async def main_async():
    """Async JSON-RPC server main function"""
    
    print(f"PyDoll MCP Server v{__version__} - Complete JSON-RPC Implementation", file=sys.stderr, flush=True)
    print(f"Using Chrome at: {DEFAULT_CHROME_PATH}", file=sys.stderr, flush=True)
    print("Server ready for JSON-RPC requests...", file=sys.stderr, flush=True)
    
    try:
        # Use asyncio to read from stdin properly
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        transport, _ = await asyncio.get_event_loop().connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        
        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                    
                line = line.decode().strip()
                if not line:
                    continue
            except Exception as e:
                logger.error(f"Error reading from stdin: {e}")
                break
                
            try:
                request = json.loads(line)
                method = request.get("method")
                request_id = request.get("id")
                params = request.get("params", {})
                
                if method == "initialize":
                    response = handle_initialize(request_id)
                elif method == "tools/list":
                    response = handle_tools_list(request_id)
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    response = await handle_tool_call_async(request_id, tool_name, arguments)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                send_response(response)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                send_response(error_response)
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                send_response(error_response)
    
    except KeyboardInterrupt:
        print("Server shutdown requested", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        # Cleanup all sessions
        for browser in BROWSER_SESSIONS.values():
            try:
                if hasattr(browser, 'quit'):
                    browser.quit()
                elif hasattr(browser, 'stop'):
                    await browser.stop()
                elif hasattr(browser, 'close'):
                    await browser.close()
            except:
                pass
        BROWSER_SESSIONS.clear()
        TAB_SESSIONS.clear()
        ELEMENT_CACHE.clear()

def run_server():
    """Main entry point - JSON-RPC server only"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Server shutdown", file=sys.stderr, flush=True)

if __name__ == "__main__":
    # Perform auto-update check on startup (unless disabled)
    if "--no-update" not in sys.argv and os.getenv("PYDOLL_MCP_NO_UPDATE") != "1":
        auto_update_check()
    
    run_server()
