"""
Test MCP protocol compliance and JSON-RPC communication.
"""
import json
import pytest
from unittest.mock import patch, AsyncMock


class TestMCPProtocol:
    """Test MCP protocol implementation."""

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_client, sample_list_tools_request):
        """Test tools/list method returns all available tools."""
        response = await mcp_client.send_request(sample_list_tools_request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == sample_list_tools_request["id"]
        assert "result" in response
        assert "tools" in response["result"]
        
        tools = response["result"]["tools"]
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for key browser automation tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "mcp__pydoll-browser__create_browser_session",
            "mcp__pydoll-browser__navigate",
            "mcp__pydoll-browser__find_elements",
            "mcp__pydoll-browser__get_page_source"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_invalid_method(self, mcp_client):
        """Test server handles invalid method gracefully."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid/method"
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found

    @pytest.mark.asyncio
    async def test_malformed_request(self, mcp_client):
        """Test server handles malformed requests."""
        # Missing required fields
        request = {
            "jsonrpc": "2.0",
            # Missing id and method
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32600  # Invalid request

    @pytest.mark.asyncio
    async def test_tool_schema_validation(self, mcp_client, sample_list_tools_request):
        """Test that tool schemas are properly defined."""
        response = await mcp_client.send_request(sample_list_tools_request)
        tools = response["result"]["tools"]
        
        for tool in tools:
            # Each tool should have required fields
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # Input schema should be valid JSON Schema
            schema = tool["inputSchema"]
            assert "type" in schema
            assert schema["type"] == "object"
            
            if "properties" in schema:
                assert isinstance(schema["properties"], dict)

    def test_json_rpc_version_compliance(self, sample_tool_request):
        """Test JSON-RPC 2.0 version compliance."""
        assert sample_tool_request["jsonrpc"] == "2.0"
        assert "id" in sample_tool_request
        assert "method" in sample_tool_request

    @pytest.mark.asyncio
    async def test_error_response_format(self, mcp_client):
        """Test error responses follow JSON-RPC format."""
        request = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 42
        assert "error" in response
        
        error = response["error"]
        assert "code" in error
        assert "message" in error
        assert isinstance(error["code"], int)
        assert isinstance(error["message"], str)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mcp_client):
        """Test server handles concurrent requests properly."""
        import asyncio
        
        requests = [
            {
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/list"
            }
            for i in range(5)
        ]
        
        # Send concurrent requests
        tasks = [mcp_client.send_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # Check all responses are valid and have correct IDs
        for i, response in enumerate(responses):
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == i
            assert "result" in response or "error" in response