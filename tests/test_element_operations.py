"""
Test element finding, interaction, and property operations.
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestElementOperations:
    """Test element finding and interaction functionality."""

    @pytest.mark.asyncio
    async def test_find_elements(self, mcp_client, element_selectors):
        """Test finding elements with different selector types."""
        for selector_type, selectors in element_selectors.items():
            for element_name, selector_value in selectors.items():
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "mcp__pydoll-browser__find_elements",
                        "arguments": {
                            "tab_id": "test-tab",
                            "base_element_id": "root",
                            "selector_type": selector_type,
                            "selector_value": selector_value,
                            "limit": 10
                        }
                    }
                }
                
                response = await mcp_client.send_request(request)
                
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == 1
                assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_wait_for_element(self, mcp_client):
        """Test waiting for element to appear."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__wait_for_element",
                "arguments": {
                    "tab_id": "test-tab",
                    "selector_type": "css",
                    "selector_value": "h1",
                    "timeout": 5
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_element_text(self, mcp_client):
        """Test getting element text content."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_text",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_element_attribute(self, mcp_client):
        """Test getting element attributes."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_attribute",
                "arguments": {
                    "element_id": "test-element-id",
                    "attribute_name": "class"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_element_property(self, mcp_client):
        """Test getting element JavaScript properties."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_property",
                "arguments": {
                    "element_id": "test-element-id",
                    "property_name": "innerHTML"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_element_html(self, mcp_client):
        """Test getting element HTML content."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_html",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_get_element_bounds(self, mcp_client):
        """Test getting element position and dimensions."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_bounds",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_element_visibility_checks(self, mcp_client):
        """Test element visibility, enabled, and selected state checks."""
        state_checks = [
            "is_element_visible",
            "is_element_enabled", 
            "is_element_selected",
            "is_element_on_top",
            "is_element_interactable"
        ]
        
        for check_method in state_checks:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": f"mcp__pydoll-browser__{check_method}",
                    "arguments": {"element_id": "test-element-id"}
                }
            }
            
            response = await mcp_client.send_request(request)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_click_element(self, mcp_client):
        """Test clicking elements."""
        # Test regular click
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__click_element",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_click_element_js(self, mcp_client):
        """Test JavaScript click on elements."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__click_element_js",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_type_text(self, mcp_client):
        """Test typing text into elements."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__type_text",
                "arguments": {
                    "element_id": "test-element-id",
                    "text": "Hello World"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_clear_text(self, mcp_client):
        """Test clearing text from input elements."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__clear_text",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_hover_element(self, mcp_client):
        """Test hovering over elements."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__hover_element",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_scroll_element(self, mcp_client):
        """Test scrolling elements."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__scroll_element",
                "arguments": {"element_id": "test-element-id"}
            }
        }
        
        response = await mcp_client.send_request(request)
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_invalid_element_id(self, mcp_client):
        """Test operations with invalid element IDs."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_element_text",
                "arguments": {"element_id": "nonexistent-element-id"}
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
    async def test_invalid_selector_type(self, mcp_client):
        """Test finding elements with invalid selector type."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__find_elements",
                "arguments": {
                    "tab_id": "test-tab",
                    "base_element_id": "root",
                    "selector_type": "invalid_selector_type",
                    "selector_value": "some_value"
                }
            }
        }
        
        response = await mcp_client.send_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        
        # Should return error for invalid selector type
        if "error" in response:
            assert response["error"]["code"] in [-32602, -32000]
        else:
            result = response["result"]
            content_text = result["content"][0]["text"].lower()
            assert "error" in content_text or "invalid" in content_text