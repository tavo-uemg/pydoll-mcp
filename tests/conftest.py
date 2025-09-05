"""
Pytest configuration and shared fixtures for PyDoll MCP testing.
"""
import asyncio
import json
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_pydoll():
    """Mock PyDoll browser instance for unit testing."""
    mock = Mock()
    mock.start = AsyncMock()
    mock.close = AsyncMock()
    mock.navigate = AsyncMock()
    mock.find_element = AsyncMock()
    mock.find_elements = AsyncMock(return_value=[])
    mock.get_page_source = AsyncMock(return_value="<html></html>")
    mock.get_page_title = AsyncMock(return_value="Test Page")
    mock.get_current_url = AsyncMock(return_value="https://example.com")
    return mock


@pytest.fixture
def sample_tool_request():
    """Sample MCP tool request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "mcp__pydoll-browser__create_browser_session",
            "arguments": {
                "session_id": "test-session",
                "headless": True,
                "window_size": "1920,1080"
            }
        }
    }


@pytest.fixture
def sample_list_tools_request():
    """Sample list tools request."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }


@pytest.fixture
def test_html_content():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1 id="main-title">Test Title</h1>
        <form id="test-form">
            <input type="text" name="username" id="username" placeholder="Username">
            <input type="password" name="password" id="password" placeholder="Password">
            <button type="submit" id="submit-btn">Submit</button>
        </form>
        <div class="content">
            <p>Test paragraph 1</p>
            <p>Test paragraph 2</p>
            <a href="#" id="test-link">Test Link</a>
        </div>
    </body>
    </html>
    """


class MCPTestClient:
    """Test client for interacting with MCP server."""

    def __init__(self, server_path: str):
        self.server_path = server_path
        self.process = None

    async def start(self):
        """Start the MCP server process."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            # Give server time to start up
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Warning: Failed to start MCP server: {e}")
            raise

    async def send_request(self, request: dict) -> dict:
        """Send JSON-RPC request to server."""
        if not self.process:
            raise RuntimeError("Server not started")

        try:
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            # Wait for response with timeout
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(), 
                timeout=10.0
            )
            
            if not response_line:
                raise RuntimeError("Server closed connection")
                
            response_text = response_line.decode().strip()
            if not response_text:
                raise RuntimeError("Empty response from server")
                
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {e}")
        except asyncio.TimeoutError:
            raise RuntimeError("Server response timeout")

    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()


@pytest_asyncio.fixture
async def mcp_client() -> AsyncGenerator[MCPTestClient, None]:
    """Create and manage MCP test client."""
    server_path = Path(__file__).parent.parent / "pydoll-mcp"
    
    # Skip if server doesn't exist or isn't executable
    if not server_path.exists():
        pytest.skip(f"PyDoll MCP server not found at {server_path}")
    
    client = MCPTestClient(str(server_path))

    try:
        await client.start()
        
        # Test basic connectivity with a simple request
        try:
            test_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "tools/list"
            }
            await client.send_request(test_request)
        except Exception as e:
            pytest.skip(f"MCP server not responding: {e}")
        
        yield client
    except Exception as e:
        pytest.skip(f"Failed to start MCP server: {e}")
    finally:
        try:
            await client.stop()
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture
def browser_session_data():
    """Test data for browser session creation."""
    return {
        "session_id": "test-session-123",
        "headless": True,
        "window_size": "1920,1080",
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "disable_images": False,
        "disable_javascript": False
    }


@pytest.fixture
def element_selectors():
    """Common element selectors for testing."""
    return {
        "css": {
            "h1": "h1",
            "input": "input[type='text']",
            "button": "button",
            "form": "#test-form"
        },
        "xpath": {
            "h1": "//h1[@id='main-title']",
            "input": "//input[@name='username']",
            "button": "//button[@type='submit']"
        },
        "id": {
            "title": "main-title",
            "username": "username",
            "password": "password",
            "submit": "submit-btn"
        }
    }


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temporary files after each test."""
    temp_files = []
    yield temp_files

    # Cleanup after test
    for file_path in temp_files:
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {file_path}: {e}")


@pytest.fixture
def mock_chrome_process():
    """Mock Chrome process for testing."""
    mock = Mock()
    mock.poll = Mock(return_value=None)  # Process is running
    mock.terminate = Mock()
    mock.wait = Mock(return_value=0)
    mock.pid = 12345
    return mock
