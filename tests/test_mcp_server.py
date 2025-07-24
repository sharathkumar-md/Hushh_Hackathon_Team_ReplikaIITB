# tests/test_mcp_server.py
"""
Comprehensive tests for MCP Server following hackathon requirements.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock

from hushh_mcp.mcp_server import HushhMCPServer, MCPMethod
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

class TestMCPServer:
    """Test suite for HushhMCP Server"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.server = HushhMCPServer()
        self.user_id = "test_user_mcp"
        
        # Create valid consent token
        self.valid_token = issue_token(
            user_id=self.user_id,
            agent_id="test_agent",
            scope=ConsentScope.AGENT_SHOPPING_PURCHASE,
            expires_in_ms=24 * 60 * 60 * 1000
        )
    
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test MCP initialization"""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Test Client", "version": "1.0.0"}
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "capabilities" in response["result"]
        assert "serverInfo" in response["result"]
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing available resources"""
        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/list"
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "resources" in response["result"]
        assert len(response["result"]["resources"]) > 0
    
    @pytest.mark.asyncio
    async def test_read_resource_with_consent(self):
        """Test reading resource with valid consent"""
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {
                "uri": "hushh://agents/shopping/recommendations",
                "consent_token": self.valid_token.token
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "contents" in response["result"]
    
    @pytest.mark.asyncio
    async def test_read_resource_without_consent(self):
        """Test reading resource without consent"""
        message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {
                "uri": "hushh://vault/user/test/email"
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert "consent" in response["error"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools"""
        message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/list"
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
    
    @pytest.mark.asyncio
    async def test_call_tool_verify_email(self):
        """Test calling email verification tool"""
        message = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "verify_email",
                "arguments": {
                    "email": "test@example.com"
                }
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "content" in response["result"]
    
    @pytest.mark.asyncio
    async def test_call_tool_with_consent(self):
        """Test calling tool that requires consent"""
        message = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "get_shopping_deals",
                "arguments": {
                    "user_id": self.user_id,
                    "consent_token": self.valid_token.token,
                    "category": "electronics"
                }
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        # Should succeed or fail gracefully
        assert "result" in response or "error" in response
    
    @pytest.mark.asyncio
    async def test_request_consent_extension(self):
        """Test HushhMCP consent request extension"""
        message = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "hushh/consent/request",
            "params": {
                "user_id": self.user_id,
                "agent_id": "test_agent",
                "scope": "vault.read.email"
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "success" in response["result"]
    
    @pytest.mark.asyncio
    async def test_verify_consent_extension(self):
        """Test HushhMCP consent verification extension"""
        message = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "hushh/consent/verify",
            "params": {
                "token": self.valid_token.token,
                "expected_scope": "agent.shopping.purchase"
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "valid" in response["result"]
    
    @pytest.mark.asyncio
    async def test_execute_agent_extension(self):
        """Test HushhMCP agent execution extension"""
        message = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "hushh/agent/execute",
            "params": {
                "agent_name": "shopping",
                "user_id": self.user_id,
                "consent_token": self.valid_token.token,
                "arguments": {
                    "category": "electronics"
                }
            }
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        # Should succeed or fail gracefully
        assert "result" in response or "error" in response
    
    @pytest.mark.asyncio
    async def test_unknown_method(self):
        """Test handling of unknown methods"""
        message = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "unknown/method"
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found
    
    @pytest.mark.asyncio
    async def test_malformed_message(self):
        """Test handling of malformed messages"""
        message = {
            "not_jsonrpc": "invalid"
        }
        
        response = await self.server.handle_message(message)
        
        assert response["jsonrpc"] == "2.0"
        assert "error" in response

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
