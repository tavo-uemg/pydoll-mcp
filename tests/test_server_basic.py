"""
Basic PyDoll MCP server functionality tests.
These tests verify the server starts and responds to basic requests.
"""
import pytest


class TestServerBasic:
    """Test basic server functionality."""

    @pytest.mark.asyncio
    async def test_server_connectivity(self, mcp_client):
        """Test that the MCP server can be reached and responds."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "tools" in response["result"]
        
        # Should have browser automation tools
        tool_names = [tool["name"] for tool in response["result"]["tools"]]
        assert any("browser" in name for name in tool_names)

    @pytest.mark.asyncio
    async def test_invalid_method(self, mcp_client):
        """Test server handles invalid methods gracefully."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "invalid/method"
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found

    @pytest.mark.asyncio
    async def test_malformed_request(self, mcp_client):
        """Test server handles malformed requests."""
        request = {
            "jsonrpc": "2.0",
            # Missing id and method
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, mcp_client):
        """Test listing sessions when none exist."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__list_sessions",
                "arguments": {}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        
        if "result" in response:
            result = response["result"]
            assert "content" in result
            # Should be valid JSON content
            content_text = result["content"][0]["text"]
            import json
            session_data = json.loads(content_text)
            assert "browser_sessions" in session_data
            assert "tab_sessions" in session_data
            assert isinstance(session_data["browser_sessions"], list)
            assert isinstance(session_data["tab_sessions"], list)

    @pytest.mark.asyncio
    async def test_cleanup_elements_empty(self, mcp_client):
        """Test cleanup when no elements exist."""
        request = {
            "jsonrpc": "2.0", 
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__cleanup_elements",
                "arguments": {}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        
        if "result" in response:
            result = response["result"]
            assert "content" in result
            content_text = result["content"][0]["text"]
            assert "cleaned" in content_text.lower() or "cleanup" in content_text.lower()