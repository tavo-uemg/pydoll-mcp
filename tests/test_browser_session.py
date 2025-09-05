"""
Test browser session management functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestBrowserSession:
    """Test browser session operations."""

    @pytest.mark.asyncio
    async def test_create_browser_session(self, mcp_client, browser_session_data):
        """Test creating a new browser session."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_browser_session",
                "arguments": browser_session_data
            }
        }

        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            response = await mcp_client.send_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1

            if "result" in response:
                result = response["result"]
                assert "content" in result
                assert len(result["content"]) > 0

                content = result["content"][0]
                assert content["type"] == "text"
                assert "session" in content["text"].lower()

    @pytest.mark.asyncio
    async def test_start_browser_session(self, mcp_client):
        """Test starting a browser session."""
        # First create session
        create_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_browser_session",
                "arguments": {"session_id": "test-start-session", "headless": True}
            }
        }

        start_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__start_browser_session",
                "arguments": {"session_id": "test-start-session"}
            }
        }

        with patch('subprocess.Popen'), \
             patch('asyncio.create_subprocess_exec') as mock_subprocess:

            mock_process = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Create session first
            await mcp_client.send_request(create_request)

            # Start session
            response = await mcp_client.send_request(start_request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2

    @pytest.mark.asyncio
    async def test_list_sessions(self, mcp_client):
        """Test listing active sessions."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__list_sessions",
                "arguments": {}
            }
        }

        response = await mcp_client.send_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1

        if "result" in response:
            result = response["result"]
            assert "content" in result
            content_text = result["content"][0]["text"]

            # Should be valid JSON with session info
            import json
            session_data = json.loads(content_text)
            assert "browser_sessions" in session_data
            assert "tab_sessions" in session_data
            assert isinstance(session_data["browser_sessions"], list)
            assert isinstance(session_data["tab_sessions"], list)

    @pytest.mark.asyncio
    async def test_get_session_info(self, mcp_client):
        """Test getting specific session information."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__get_session_info",
                "arguments": {"session_id": "nonexistent-session"}
            }
        }

        response = await mcp_client.send_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1

        # Should handle nonexistent session gracefully
        if "error" in response:
            assert response["error"]["code"] in [-32000, -32001, -32002]
        else:
            # Or return empty/error content
            result = response["result"]
            assert "content" in result

    @pytest.mark.asyncio
    async def test_close_browser_session(self, mcp_client):
        """Test closing a browser session."""
        # Test closing nonexistent session
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__close_browser_session",
                "arguments": {"session_id": "nonexistent-session"}
            }
        }

        response = await mcp_client.send_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1

        # Should handle gracefully
        assert "result" in response or "error" in response

    @pytest.mark.asyncio
    async def test_invalid_session_parameters(self, mcp_client):
        """Test creating session with invalid parameters."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_browser_session",
                "arguments": {
                    # Missing required session_id
                    "headless": True,
                    "window_size": "invalid_size_format"
                }
            }
        }

        response = await mcp_client.send_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1

        # Should return error for missing required parameters
        if "error" in response:
            assert response["error"]["code"] in [-32602, -32000]  # Invalid params
        else:
            # Or handle gracefully with error content
            result = response["result"]
            content_text = result["content"][0]["text"].lower()
            assert "error" in content_text or "invalid" in content_text

    @pytest.mark.asyncio
    async def test_cleanup_elements(self, mcp_client):
        """Test element cleanup functionality."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__cleanup_elements",
                "arguments": {}
            }
        }

        response = await mcp_client.send_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1

        if "result" in response:
            result = response["result"]
            assert "content" in result
            content_text = result["content"][0]["text"]
            assert "cleaned" in content_text.lower() or "cleanup" in content_text.lower()

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, mcp_client):
        """Test complete session lifecycle: create -> start -> use -> close."""
        session_id = "lifecycle-test-session"

        # 1. Create session
        create_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__create_browser_session",
                "arguments": {"session_id": session_id, "headless": True}
            }
        }

        # 2. Start session
        start_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__start_browser_session",
                "arguments": {"session_id": session_id}
            }
        }

        # 3. Check session exists
        list_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__list_sessions",
                "arguments": {}
            }
        }

        # 4. Close session
        close_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "mcp__pydoll-browser__close_browser_session",
                "arguments": {"session_id": session_id}
            }
        }

        with patch('subprocess.Popen'), \
             patch('asyncio.create_subprocess_exec'):

            # Execute lifecycle
            create_response = await mcp_client.send_request(create_request)
            assert "result" in create_response or "error" in create_response

            start_response = await mcp_client.send_request(start_request)
            assert "result" in start_response or "error" in start_response

            list_response = await mcp_client.send_request(list_request)
            assert "result" in list_response

            close_response = await mcp_client.send_request(close_request)
            assert "result" in close_response or "error" in close_response
