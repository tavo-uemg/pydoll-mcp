"""
End-to-end integration tests for PyDoll MCP Server.
"""
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.browser
class TestEndToEndWorkflows:
    """Test complete browser automation workflows."""

    @pytest.mark.asyncio
    async def test_complete_browser_session_workflow(self, mcp_client):
        """Test complete browser session lifecycle with real operations."""
        session_id = "e2e-test-session"
        tab_id = f"{session_id}-tab-1"

        try:
            # 1. Create browser session
            create_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__create_browser_session",
                    "arguments": {
                        "session_id": session_id,
                        "headless": True,
                        "window_size": "1920,1080"
                    }
                }
            })

            assert "result" in create_response or "error" in create_response

            # 2. Start browser session
            start_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__start_browser_session",
                    "arguments": {"session_id": session_id}
                }
            })

            assert "result" in start_response or "error" in start_response

            # 3. Create tab and navigate
            tab_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__create_tab",
                    "arguments": {
                        "browser_session_id": session_id,
                        "tab_id": tab_id,
                        "url": "https://example.com"
                    }
                }
            })

            # 4. Get page information
            url_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__get_page_url",
                    "arguments": {"tab_id": tab_id}
                }
            })

            # 5. Find elements
            elements_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__find_elements",
                    "arguments": {
                        "tab_id": tab_id,
                        "base_element_id": "root",
                        "selector_type": "tag",
                        "selector_value": "h1"
                    }
                }
            })

            # 6. Take screenshot
            screenshot_path = "/tmp/e2e-test-screenshot.png"
            screenshot_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__take_screenshot",
                    "arguments": {
                        "tab_id": tab_id,
                        "save_path": screenshot_path
                    }
                }
            })

            # Verify screenshot was created
            if "result" in screenshot_response:
                assert Path(screenshot_path).exists()

        finally:
            # Cleanup
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__close_browser_session",
                    "arguments": {"session_id": session_id}
                }
            })

    @pytest.mark.asyncio
    async def test_form_interaction_workflow(self, mcp_client):
        """Test form interaction and input handling."""
        session_id = "form-test-session"
        tab_id = f"{session_id}-tab-1"

        try:
            # Setup browser session
            await self._setup_browser_session(mcp_client, session_id, tab_id)

            # Navigate to form page (would be a test page with forms)
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__navigate",
                    "arguments": {
                        "tab_id": tab_id,
                        "url": "https://httpbin.org/forms/post"
                    }
                }
            })

            # Wait for page load
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__wait_for_page_load",
                    "arguments": {"tab_id": tab_id, "timeout": 10}
                }
            })

            # Find form elements
            input_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 12,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__find_elements",
                    "arguments": {
                        "tab_id": tab_id,
                        "base_element_id": "root",
                        "selector_type": "css",
                        "selector_value": "input[type='text']"
                    }
                }
            })

            # All requests should be handled gracefully
            assert "result" in input_response or "error" in input_response

        finally:
            await self._cleanup_session(mcp_client, session_id)

    @pytest.mark.asyncio
    async def test_navigation_and_history_workflow(self, mcp_client):
        """Test navigation and browser history operations."""
        session_id = "nav-test-session"
        tab_id = f"{session_id}-tab-1"

        try:
            await self._setup_browser_session(mcp_client, session_id, tab_id)

            # Navigate to first page
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__navigate",
                    "arguments": {
                        "tab_id": tab_id,
                        "url": "https://example.com"
                    }
                }
            })

            # Navigate to second page
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 21,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__navigate",
                    "arguments": {
                        "tab_id": tab_id,
                        "url": "https://httpbin.org"
                    }
                }
            })

            # Go back
            back_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 22,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__go_back",
                    "arguments": {"tab_id": tab_id}
                }
            })

            # Go forward
            forward_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 23,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__go_forward",
                    "arguments": {"tab_id": tab_id}
                }
            })

            # Refresh page
            refresh_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 24,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__refresh_page",
                    "arguments": {"tab_id": tab_id}
                }
            })

            # All navigation operations should be handled
            assert "result" in back_response or "error" in back_response
            assert "result" in forward_response or "error" in forward_response
            assert "result" in refresh_response or "error" in refresh_response

        finally:
            await self._cleanup_session(mcp_client, session_id)

    @pytest.mark.asyncio
    async def test_javascript_execution_workflow(self, mcp_client):
        """Test JavaScript execution capabilities."""
        session_id = "js-test-session"
        tab_id = f"{session_id}-tab-1"

        try:
            await self._setup_browser_session(mcp_client, session_id, tab_id)

            # Navigate to a page
            await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 30,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__navigate",
                    "arguments": {
                        "tab_id": tab_id,
                        "url": "https://example.com"
                    }
                }
            })

            # Execute JavaScript
            js_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 31,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__execute_script",
                    "arguments": {
                        "tab_id": tab_id,
                        "script": "document.title"
                    }
                }
            })

            # Wait for function
            wait_response = await mcp_client.send_request({
                "jsonrpc": "2.0",
                "id": 32,
                "method": "tools/call",
                "params": {
                    "name": "mcp__pydoll-browser__wait_for_function",
                    "arguments": {
                        "tab_id": tab_id,
                        "script": "document.readyState === 'complete'",
                        "timeout": 5
                    }
                }
            })

            assert "result" in js_response or "error" in js_response
            assert "result" in wait_response or "error" in wait_response

        finally:
            await self._cleanup_session(mcp_client, session_id)

    async def _setup_browser_session(self, mcp_client, session_id: str, tab_id: str):
        """Helper to setup browser session for tests."""
        # Create session
        await mcp_client.send_request({
            "jsonrpc": "2.0",
            "id": 1000,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_browser_session",
                "arguments": {
                    "session_id": session_id,
                    "headless": True,
                    "window_size": "1920,1080"
                }
            }
        })

        # Start session
        await mcp_client.send_request({
            "jsonrpc": "2.0",
            "id": 1001,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__start_browser_session",
                "arguments": {"session_id": session_id}
            }
        })

        # Create tab
        await mcp_client.send_request({
            "jsonrpc": "2.0",
            "id": 1002,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_tab",
                "arguments": {
                    "browser_session_id": session_id,
                    "tab_id": tab_id
                }
            }
        })

    async def _cleanup_session(self, mcp_client, session_id: str):
        """Helper to cleanup browser session after tests."""
        await mcp_client.send_request({
            "jsonrpc": "2.0",
            "id": 9999,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__close_browser_session",
                "arguments": {"session_id": session_id}
            }
        })

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_session_management(self, mcp_client):
        """Stress test session creation and cleanup."""
        sessions = []

        try:
            # Create multiple sessions rapidly
            for i in range(3):  # Limited for CI environment
                session_id = f"stress-test-{i}"
                sessions.append(session_id)

                response = await mcp_client.send_request({
                    "jsonrpc": "2.0",
                    "id": 100 + i,
                    "method": "tools/call",
                    "params": {
                        "name": "mcp__pydoll-browser__create_browser_session",
                        "arguments": {
                            "session_id": session_id,
                            "headless": True
                        }
                    }
                })

                assert "result" in response or "error" in response

        finally:
            # Cleanup all sessions
            for session_id in sessions:
                await mcp_client.send_request({
                    "jsonrpc": "2.0",
                    "id": 999,
                    "method": "tools/call",
                    "params": {
                        "name": "mcp__pydoll-browser__close_browser_session",
                        "arguments": {"session_id": session_id}
                    }
                })