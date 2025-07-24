# tests/test_ai_assistant_agent.py
"""
Comprehensive tests for HushhAIAssistant following hackathon requirements.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from hushh_mcp.agents.ai_assistant import HushhAIAssistant
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

class TestAIAssistantAgent:
    """Test suite for HushhAIAssistant"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = HushhAIAssistant()
        self.user_id = "test_user_ai"
        self.agent_id = "hushh_ai_assistant"
        
        # Create valid consent token
        self.valid_token = issue_token(
            user_id=self.user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=24 * 60 * 60 * 1000
        )
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent.agent_id == "hushh_ai_assistant"
        assert len(self.agent.required_scopes) > 0
    
    def test_basic_query_execution(self):
        """Test basic query execution with valid consent"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token,
            query="What is the weather today?",
            task_type="general_assistance"
        )
        
        assert result.success is True
        assert result.data is not None
        assert "response" in result.data
        assert result.agent_id == self.agent_id
    
    def test_invalid_consent_handling(self):
        """Test handling of invalid consent tokens"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str="invalid_token",
            query="Test query"
        )
        
        assert result.success is False
        assert result.error is not None
    
    def test_fallback_response(self):
        """Test fallback response when LLM unavailable"""
        with patch('requests.post', side_effect=Exception("LLM unavailable")):
            result = self.agent.execute(
                user_id=self.user_id,
                token_str=self.valid_token.token,
                query="Test query"
            )
            
            assert result.success is True  # Should fall back gracefully
            assert "fallback" in result.data["response"].lower() or "unable" in result.data["response"].lower()
    
    def test_context_handling(self):
        """Test context preservation across queries"""
        context = {"previous_topic": "shopping", "user_preferences": ["tech", "books"]}
        
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token,
            query="Continue our discussion",
            context=context
        )
        
        assert result.success is True
        assert result.data is not None
    
    def test_different_task_types(self):
        """Test different task types"""
        task_types = ["general_assistance", "question_answering", "creative_writing", "data_analysis"]
        
        for task_type in task_types:
            result = self.agent.execute(
                user_id=self.user_id,
                token_str=self.valid_token.token,
                query=f"Test {task_type} query",
                task_type=task_type
            )
            
            assert result.success is True
            assert result.data is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
