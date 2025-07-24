# hushh_mcp/mcp_server.py
"""
Model Context Protocol (MCP) Server implementation for HushhMCP.

This implements the official MCP protocol specification for agent-to-agent communication
while maintaining our consent-first architecture.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from hushh_mcp.agents.consent_utils import consent_manager
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, AgentID, HushhConsentToken

logger = logging.getLogger(__name__)

class MCPMessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class MCPMethod(str, Enum):
    # Core MCP methods
    INITIALIZE = "initialize"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    
    # HushhMCP extensions
    REQUEST_CONSENT = "hushh/consent/request"
    VERIFY_CONSENT = "hushh/consent/verify"
    REVOKE_CONSENT = "hushh/consent/revoke"
    EXECUTE_AGENT = "hushh/agent/execute"

@dataclass
class MCPMessage:
    """Standard MCP message structure"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class HushhMCPServer:
    """
    MCP Server implementing consent-first agent communication.
    
    This server allows agents to communicate while respecting user consent
    and maintaining security boundaries.
    """
    
    def __init__(self):
        self.capabilities = {
            "resources": {
                "subscribe": True,
                "list_changed": True
            },
            "tools": {
                "list_changed": True
            },
            "prompts": {
                "list_changed": True
            },
            "experimental": {
                "hushh_consent": True,
                "bacterial_code": True
            }
        }
        
        self.resources = self._initialize_resources()
        self.tools = self._initialize_tools()
        self.prompts = self._initialize_prompts()
        
    def _initialize_resources(self) -> List[Dict[str, Any]]:
        """Initialize available resources with consent requirements"""
        return [
            {
                "uri": "hushh://vault/user/{user_id}/email",
                "name": "User Email Data",
                "description": "User's email data from encrypted vault",
                "required_scope": ConsentScope.VAULT_READ_EMAIL.value,
                "mimeType": "application/json"
            },
            {
                "uri": "hushh://vault/user/{user_id}/finance",
                "name": "User Financial Data", 
                "description": "User's financial data from encrypted vault",
                "required_scope": ConsentScope.VAULT_READ_FINANCE.value,
                "mimeType": "application/json"
            },
            {
                "uri": "hushh://agents/shopping/recommendations",
                "name": "Shopping Recommendations",
                "description": "Personalized shopping recommendations",
                "required_scope": ConsentScope.AGENT_SHOPPING_PURCHASE.value,
                "mimeType": "application/json"
            }
        ]
    
    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """Initialize available tools with consent requirements"""
        return [
            {
                "name": "verify_email",
                "description": "Verify if an email address is valid",
                "required_scope": None,  # No consent needed for validation
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address to validate"
                        }
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "get_shopping_deals",
                "description": "Get personalized shopping deals for user",
                "required_scope": ConsentScope.AGENT_SHOPPING_PURCHASE.value,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "consent_token": {"type": "string"},
                        "category": {"type": "string", "enum": ["electronics", "fashion", "food", "books"]}
                    },
                    "required": ["user_id", "consent_token"]
                }
            },
            {
                "name": "encrypt_data",
                "description": "Encrypt user data for vault storage",
                "required_scope": ConsentScope.CUSTOM_SESSION_WRITE.value,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string"},
                        "user_id": {"type": "string"},
                        "consent_token": {"type": "string"}
                    },
                    "required": ["data", "user_id", "consent_token"]
                }
            }
        ]
    
    def _initialize_prompts(self) -> List[Dict[str, Any]]:
        """Initialize available prompts for agent coordination"""
        return [
            {
                "name": "consent_request",
                "description": "Generate user-friendly consent request message",
                "arguments": [
                    {
                        "name": "agent_name",
                        "description": "Name of the requesting agent",
                        "required": True
                    },
                    {
                        "name": "scope",
                        "description": "Requested consent scope",
                        "required": True
                    }
                ]
            },
            {
                "name": "shopping_recommendation",
                "description": "Generate shopping recommendation based on user data",
                "arguments": [
                    {
                        "name": "user_preferences",
                        "description": "User shopping preferences",
                        "required": True
                    },
                    {
                        "name": "budget",
                        "description": "User budget constraints",
                        "required": False
                    }
                ]
            }
        ]
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main message handler for MCP protocol.
        
        Implements consent-first request processing.
        """
        try:
            mcp_msg = MCPMessage(**message)
            
            if mcp_msg.method == MCPMethod.INITIALIZE:
                return await self._handle_initialize(mcp_msg)
            elif mcp_msg.method == MCPMethod.LIST_RESOURCES:
                return await self._handle_list_resources(mcp_msg)
            elif mcp_msg.method == MCPMethod.READ_RESOURCE:
                return await self._handle_read_resource(mcp_msg)
            elif mcp_msg.method == MCPMethod.LIST_TOOLS:
                return await self._handle_list_tools(mcp_msg)
            elif mcp_msg.method == MCPMethod.CALL_TOOL:
                return await self._handle_call_tool(mcp_msg)
            elif mcp_msg.method == MCPMethod.LIST_PROMPTS:
                return await self._handle_list_prompts(mcp_msg)
            elif mcp_msg.method == MCPMethod.GET_PROMPT:
                return await self._handle_get_prompt(mcp_msg)
            elif mcp_msg.method == MCPMethod.REQUEST_CONSENT:
                return await self._handle_request_consent(mcp_msg)
            elif mcp_msg.method == MCPMethod.VERIFY_CONSENT:
                return await self._handle_verify_consent(mcp_msg)
            elif mcp_msg.method == MCPMethod.EXECUTE_AGENT:
                return await self._handle_execute_agent(mcp_msg)
            else:
                return self._error_response(mcp_msg.id, -32601, f"Method not found: {mcp_msg.method}")
                
        except Exception as e:
            logger.error(f"MCP message handling error: {str(e)}", exc_info=True)
            return self._error_response(message.get("id"), -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, msg: MCPMessage) -> Dict[str, Any]:
        """Handle MCP initialization"""
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": self.capabilities,
                "serverInfo": {
                    "name": "HushhMCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_list_resources(self, msg: MCPMessage) -> Dict[str, Any]:
        """List available resources with consent requirements"""
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "resources": self.resources
            }
        }
    
    async def _handle_read_resource(self, msg: MCPMessage) -> Dict[str, Any]:
        """Read resource with consent validation"""
        params = msg.params or {}
        uri = params.get("uri")
        consent_token = params.get("consent_token")
        
        if not uri:
            return self._error_response(msg.id, -32602, "Missing required parameter: uri")
        
        # Find resource and check consent requirements
        resource = next((r for r in self.resources if r["uri"] == uri), None)
        if not resource:
            return self._error_response(msg.id, -32602, f"Resource not found: {uri}")
        
        if resource.get("required_scope") and not consent_token:
            return self._error_response(msg.id, -32602, "Consent token required for this resource")
        
        # Validate consent if required
        if resource.get("required_scope"):
            consent_result = consent_manager.check_consent(
                token_str=consent_token,
                expected_scope=resource["required_scope"]
            )
            if not consent_result.success:
                return self._error_response(msg.id, -32603, f"Consent validation failed: {consent_result.error}")
        
        # Return resource content (simulated for demo)
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": resource["mimeType"],
                        "text": json.dumps({
                            "data": f"Secure data from {uri}",
                            "accessed_at": "2025-07-24T12:00:00Z",
                            "consent_verified": True
                        })
                    }
                ]
            }
        }
    
    async def _handle_list_tools(self, msg: MCPMessage) -> Dict[str, Any]:
        """List available tools"""
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "tools": self.tools
            }
        }
    
    async def _handle_call_tool(self, msg: MCPMessage) -> Dict[str, Any]:
        """Execute tool with consent validation"""
        params = msg.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return self._error_response(msg.id, -32602, "Missing required parameter: name")
        
        # Find tool
        tool = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool:
            return self._error_response(msg.id, -32602, f"Tool not found: {tool_name}")
        
        # Validate consent if required
        if tool.get("required_scope"):
            consent_token = arguments.get("consent_token")
            if not consent_token:
                return self._error_response(msg.id, -32602, "Consent token required for this tool")
            
            consent_result = consent_manager.check_consent(
                token_str=consent_token,
                expected_scope=tool["required_scope"]
            )
            if not consent_result.success:
                return self._error_response(msg.id, -32603, f"Consent validation failed: {consent_result.error}")
        
        # Execute tool
        try:
            result = await self._execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg.id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result)
                        }
                    ]
                }
            }
        except Exception as e:
            return self._error_response(msg.id, -32603, f"Tool execution failed: {str(e)}")
    
    async def _handle_list_prompts(self, msg: MCPMessage) -> Dict[str, Any]:
        """List available prompts"""
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "prompts": self.prompts
            }
        }
    
    async def _handle_get_prompt(self, msg: MCPMessage) -> Dict[str, Any]:
        """Get specific prompt with parameters"""
        params = msg.params or {}
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not prompt_name:
            return self._error_response(msg.id, -32602, "Missing required parameter: name")
        
        prompt = next((p for p in self.prompts if p["name"] == prompt_name), None)
        if not prompt:
            return self._error_response(msg.id, -32602, f"Prompt not found: {prompt_name}")
        
        # Generate prompt content
        content = await self._generate_prompt(prompt_name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "description": prompt["description"],
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": content
                        }
                    }
                ]
            }
        }
    
    async def _handle_request_consent(self, msg: MCPMessage) -> Dict[str, Any]:
        """Handle consent request (HushhMCP extension)"""
        params = msg.params or {}
        user_id = params.get("user_id")
        agent_id = params.get("agent_id")
        scope = params.get("scope")
        
        if not all([user_id, agent_id, scope]):
            return self._error_response(msg.id, -32602, "Missing required parameters")
        
        result = consent_manager.request_consent(user_id, agent_id, scope)
        
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "success": result.success,
                "token": result.data.get("token") if result.success else None,
                "error": result.error if not result.success else None
            }
        }
    
    async def _handle_verify_consent(self, msg: MCPMessage) -> Dict[str, Any]:
        """Handle consent verification (HushhMCP extension)"""
        params = msg.params or {}
        token = params.get("token")
        expected_scope = params.get("expected_scope")
        
        if not token:
            return self._error_response(msg.id, -32602, "Missing required parameter: token")
        
        result = consent_manager.check_consent(token, expected_scope)
        
        return {
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "valid": result.success,
                "details": result.data if result.success else None,
                "error": result.error if not result.success else None
            }
        }
    
    async def _handle_execute_agent(self, msg: MCPMessage) -> Dict[str, Any]:
        """Handle agent execution (HushhMCP extension)"""
        params = msg.params or {}
        agent_name = params.get("agent_name")
        user_id = params.get("user_id")
        consent_token = params.get("consent_token")
        arguments = params.get("arguments", {})
        
        if not all([agent_name, user_id, consent_token]):
            return self._error_response(msg.id, -32602, "Missing required parameters")
        
        # Execute agent with consent validation
        try:
            if agent_name == "shopping":
                from hushh_mcp.agents.shopping import HushhShoppingAgent
                agent = HushhShoppingAgent()
                result = agent.execute(user_id, consent_token, **arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg.id,
                    "result": {
                        "success": result.success,
                        "data": result.data,
                        "agent_id": result.agent_id
                    }
                }
            else:
                return self._error_response(msg.id, -32602, f"Unknown agent: {agent_name}")
                
        except Exception as e:
            return self._error_response(msg.id, -32603, f"Agent execution failed: {str(e)}")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tool"""
        if tool_name == "verify_email":
            from hushh_mcp.operons.verify_email import verify_user_email
            email = arguments.get("email")
            return {
                "valid": verify_user_email(email),
                "email": email
            }
        
        elif tool_name == "get_shopping_deals":
            from hushh_mcp.agents.shopping import HushhShoppingAgent
            agent = HushhShoppingAgent()
            result = agent.execute(
                arguments["user_id"],
                arguments["consent_token"],
                category=arguments.get("category")
            )
            return result.data if result.success else {"error": result.error}
        
        elif tool_name == "encrypt_data":
            from hushh_mcp.vault.encrypt import encrypt_data
            from hushh_mcp.config import VAULT_ENCRYPTION_KEY
            encrypted = encrypt_data(arguments["data"], VAULT_ENCRYPTION_KEY)
            return {
                "encrypted": True,
                "algorithm": encrypted.algorithm,
                "encoding": encrypted.encoding
            }
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _generate_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> str:
        """Generate prompt content"""
        if prompt_name == "consent_request":
            agent_name = arguments.get("agent_name", "Unknown Agent")
            scope = arguments.get("scope", "unspecified")
            return f"The {agent_name} is requesting permission to access your {scope} data. This will allow the agent to provide personalized recommendations. Do you consent to this access?"
        
        elif prompt_name == "shopping_recommendation":
            preferences = arguments.get("user_preferences", "general")
            budget = arguments.get("budget", "unlimited")
            return f"Generate shopping recommendations for a user with preferences: {preferences} and budget: {budget}. Focus on value and relevance."
        
        else:
            return f"Prompt: {prompt_name} with arguments: {arguments}"
    
    def _error_response(self, msg_id: Optional[Union[str, int]], code: int, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }

# Global MCP server instance
mcp_server = HushhMCPServer()

async def start_mcp_server(host: str = "localhost", port: int = 8765):
    """Start the MCP server"""
    import websockets
    
    async def handle_client(websocket, path):
        logger.info(f"MCP client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await mcp_server.handle_message(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = mcp_server._error_response(None, -32700, "Parse error")
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"MCP client disconnected: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"MCP client error: {str(e)}", exc_info=True)
    
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"🔗 MCP Server running on ws://{host}:{port}")
    return server

if __name__ == "__main__":
    # Test the MCP server
    async def test_mcp():
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            }
        }
        response = await mcp_server.handle_message(message)
        print("MCP Server Test:")
        print(json.dumps(response, indent=2))
    
    asyncio.run(test_mcp())
