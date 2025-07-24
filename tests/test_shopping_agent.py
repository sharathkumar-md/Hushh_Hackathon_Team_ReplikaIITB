# tests/test_shopping_agent.py
"""
Comprehensive tests for HushhShoppingAgent following hackathon requirements.
Tests all functionality including consent validation, ML recommendations, and error handling.
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from hushh_mcp.agents.shopping import HushhShoppingAgent
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, AgentID, HushhConsentToken
from hushh_mcp.vault.storage import store_data, retrieve_data

class TestShoppingAgent:
    """Test suite for HushhShoppingAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = HushhShoppingAgent()
        self.user_id = "test_user_shopping"
        self.agent_id = "agent_shopper"
        
        # Create valid consent token
        self.valid_token = issue_token(
            user_id=self.user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.AGENT_SHOPPING_PURCHASE,
            expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
        )
        
        # Store test user data in vault
        test_user_data = {
            "email_patterns": {
                "brands": ["apple", "nike", "uniqlo"],
                "categories": ["electronics", "fashion"],
                "price_range": "medium"
            },
            "purchase_history": [
                {"item": "iPhone 15", "price": 999, "category": "electronics"},
                {"item": "Nike Shoes", "price": 120, "category": "fashion"}
            ],
            "preferences": {
                "sustainability": True,
                "brand_loyalty": "medium",
                "deal_threshold": 0.2
            }
        }
        store_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=test_user_data,
            agent_id=self.agent_id
        )
    
    def test_agent_initialization(self):
        """Test agent initialization with correct parameters"""
        assert self.agent.agent_id == "agent_shopper"
        assert ConsentScope.VAULT_READ_EMAIL in self.agent.required_scopes
        assert ConsentScope.AGENT_SHOPPING_PURCHASE in self.agent.required_scopes
    
    def test_valid_consent_execution(self):
        """Test agent execution with valid consent token"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        assert result.data is not None
        assert "deals" in result.data
        assert "personalization_level" in result.data
        assert result.agent_id == self.agent_id
        assert result.user_id == self.user_id
        assert result.execution_time_ms is not None
    
    def test_invalid_consent_token(self):
        """Test agent execution with invalid consent token"""
        invalid_token = "hushhconsent:invalid_token_data"
        
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=invalid_token
        )
        
        assert result.success is False
        assert "consent" in result.error.lower() or "token" in result.error.lower()
        assert result.data is None
    
    def test_expired_consent_token(self):
        """Test agent execution with expired consent token"""
        # Create expired token
        expired_token = issue_token(
            user_id=self.user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.AGENT_SHOPPING_PURCHASE,
            expires_in_ms=-1000  # Already expired
        )
        
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=expired_token.token
        )
        
        assert result.success is False
        assert "expired" in result.error.lower() or "invalid" in result.error.lower()
    
    def test_wrong_scope_consent(self):
        """Test agent execution with wrong scope consent"""
        wrong_scope_token = issue_token(
            user_id=self.user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.VAULT_READ_FINANCE,  # Wrong scope
            expires_in_ms=24 * 60 * 60 * 1000
        )
        
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=wrong_scope_token.token
        )
        
        assert result.success is False
        assert "scope" in result.error.lower() or "permission" in result.error.lower()
    
    def test_personalized_recommendations(self):
        """Test personalized recommendations with user profile"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        assert result.data["personalization_level"] == "high"
        
        deals = result.data["deals"]
        assert len(deals) > 0
        
        # Check if deals have ML-style scoring
        for deal in deals:
            assert "final_score" in deal or "compatibility_score" in deal
            assert "savings" in deal
            assert "title" in deal
    
    def test_fallback_recommendations(self):
        """Test fallback recommendations when user data unavailable"""
        # Test with user that has no stored data
        new_user_id = "user_no_data"
        new_token = issue_token(
            user_id=new_user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.AGENT_SHOPPING_PURCHASE,
            expires_in_ms=24 * 60 * 60 * 1000
        )
        
        result = self.agent.execute(
            user_id=new_user_id,
            token_str=new_token.token
        )
        
        assert result.success is True
        assert result.data["personalization_level"] == "basic"
        assert len(result.data["deals"]) > 0
    
    def test_category_filtering(self):
        """Test category-specific recommendations"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token,
            category="electronics"
        )
        
        assert result.success is True
        deals = result.data["deals"]
        
        # Check if deals are filtered by category
        electronics_deals = [d for d in deals if d.get("category") == "electronics"]
        assert len(electronics_deals) > 0
    
    def test_ml_scoring_algorithm(self):
        """Test ML-style scoring algorithm"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        deals = result.data["deals"]
        
        # Verify scoring components
        for deal in deals[:3]:  # Check first 3 deals
            assert "final_score" in deal
            score = deal["final_score"]
            assert 0.0 <= score <= 1.0  # Score should be normalized
    
    def test_user_preferences_integration(self):
        """Test integration with user preferences from vault"""
        # The agent should use stored user preferences
        user_profile = self.agent._get_user_shopping_profile(
            self.user_id, 
            self.valid_token
        )
        
        assert user_profile is not None
        assert "preferred_categories" in user_profile
        assert "brand_preferences" in user_profile
        assert "price_sensitivity" in user_profile
    
    def test_deal_ranking(self):
        """Test that deals are properly ranked by score"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        deals = result.data["deals"]
        
        # Check if deals are sorted by score (descending)
        scores = [deal.get("final_score", 0) for deal in deals]
        assert scores == sorted(scores, reverse=True)
    
    def test_error_handling_with_vault_failure(self):
        """Test error handling when vault access fails"""
        with patch('hushh_mcp.vault.storage.retrieve_data', side_effect=Exception("Vault error")):
            result = self.agent.execute(
                user_id=self.user_id,
                token_str=self.valid_token.token
            )
            
            # Should still work with fallback
            assert result.success is True
            assert result.data["personalization_level"] == "basic"
    
    def test_performance_timing(self):
        """Test that execution time is recorded"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        assert result.execution_time_ms is not None
        assert result.execution_time_ms > 0
        assert result.execution_time_ms < 5000  # Should complete in under 5 seconds
    
    def test_response_format(self):
        """Test standardized response format"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        # Check AgentResponse format
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')
        assert hasattr(result, 'error')
        assert hasattr(result, 'agent_id')
        assert hasattr(result, 'user_id')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'execution_time_ms')
        
        # Check timestamp is recent
        current_time = int(time.time() * 1000)
        assert abs(current_time - result.timestamp) < 10000  # Within 10 seconds
    
    def test_savings_calculation(self):
        """Test that total savings are calculated correctly"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        
        deals = result.data["deals"]
        estimated_savings = result.data["estimated_savings"]
        
        calculated_savings = sum(deal.get("savings", 0) for deal in deals)
        assert estimated_savings == calculated_savings
    
    def test_multiple_concurrent_executions(self):
        """Test thread safety with multiple concurrent executions"""
        import threading
        import concurrent.futures
        
        def execute_agent():
            return self.agent.execute(
                user_id=self.user_id,
                token_str=self.valid_token.token
            )
        
        # Run multiple executions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_agent) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # All executions should succeed
        for result in results:
            assert result.success is True
            assert result.data is not None
    
    def test_user_id_validation(self):
        """Test user ID validation in responses"""
        result = self.agent.execute(
            user_id=self.user_id,
            token_str=self.valid_token.token
        )
        
        assert result.success is True
        assert result.user_id == self.user_id
        
        # Test with different user ID (should fail)
        different_user_token = issue_token(
            user_id="different_user",
            agent_id=self.agent_id,
            scope=ConsentScope.AGENT_SHOPPING_PURCHASE,
            expires_in_ms=24 * 60 * 60 * 1000
        )
        
        result = self.agent.execute(
            user_id=self.user_id,  # Different from token
            token_str=different_user_token.token
        )
        
        assert result.success is False
    
    def teardown_method(self):
        """Cleanup after tests"""
        # Clean up test data if needed
        pass

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
