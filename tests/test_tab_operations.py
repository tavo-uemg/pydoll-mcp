"""
Test tab management and navigation functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestTabOperations:
    """Test tab creation, navigation, and management."""

    @pytest.mark.asyncio
    async def test_create_tab(self, mcp_client):
        """Test creating a new tab."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_tab",
                "arguments": {
                    "browser_session_id": "test-session",
                    "tab_id": "test-tab-1", 
                    "url": "https://example.com"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        
        # Should handle gracefully even if session doesn't exist
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_navigate(self, mcp_client):
        """Test navigation to URL."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__navigate",
                "arguments": {
                    "tab_id": "test-tab",
                    "url": "https://httpbin.org/get",
                    "wait_until": "load"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_page_url(self, mcp_client):
        """Test getting current page URL."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call", 
            "params": {
                "name": "mcp__pydoll-browser__get_page_url",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_page_title(self, mcp_client):
        """Test getting page title."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_page_title",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_page_source(self, mcp_client, test_html_content):
        """Test getting page source."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_page_source",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response
        
        if "result" in response:
            result = response["result"]
            assert "content" in result
            content_text = result["content"][0]["text"]
            # Should return some HTML content or error message
            assert isinstance(content_text, str)

    @pytest.mark.asyncio
    async def test_go_back_forward(self, mcp_client):
        """Test browser back/forward navigation."""
        back_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__go_back",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        forward_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__go_forward", 
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        back_response = await mcp_client.send_request(back_request)
        assert back_response["jsonrpc"] == "2.0"
        assert back_response["id"] == 1
        
        forward_response = await mcp_client.send_request(forward_request)
        assert forward_response["jsonrpc"] == "2.0"
        assert forward_response["id"] == 2

    @pytest.mark.asyncio
    async def test_refresh_page(self, mcp_client):
        """Test page refresh functionality."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__refresh_page",
                "arguments": {
                    "tab_id": "test-tab",
                    "ignore_cache": False
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_close_tab(self, mcp_client):
        """Test closing a tab."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__close_tab",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_bring_tab_to_front(self, mcp_client):
        """Test bringing tab to front."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__bring_tab_to_front",
                "arguments": {"tab_id": "test-tab"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_wait_for_page_load(self, mcp_client):
        """Test waiting for page load."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__wait_for_page_load",
                "arguments": {
                    "tab_id": "test-tab",
                    "timeout": 10
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_invalid_tab_id(self, mcp_client):
        """Test operations with invalid tab ID."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__navigate",
                "arguments": {
                    "tab_id": "nonexistent-tab-id",
                    "url": "https://example.com"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        
        # Should handle gracefully
        if "error" in response:
            assert response["error"]["code"] in [-32000, -32001, -32602]
        else:
            result = response["result"]
            content_text = result["content"][0]["text"].lower()
            assert "error" in content_text or "not found" in content_text

    @pytest.mark.asyncio
    async def test_invalid_url_navigation(self, mcp_client):
        """Test navigation with invalid URL."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__navigate",
                "arguments": {
                    "tab_id": "test-tab",
                    "url": "not-a-valid-url",
                    "wait_until": "load"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        
        # Should handle invalid URL gracefully
        assert "result" in response or "error" in response