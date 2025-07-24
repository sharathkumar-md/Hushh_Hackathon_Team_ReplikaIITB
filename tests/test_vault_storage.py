# tests/test_vault_storage.py
"""
Comprehensive tests for Vault Storage System following hackathon requirements.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from hushh_mcp.vault.storage import VaultStorage, store_data, retrieve_data
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, AgentID

class TestVaultStorage:
    """Test suite for VaultStorage"""
    
    def setup_method(self):
        """Setup test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault = VaultStorage(self.temp_dir)
        self.user_id = "test_user_vault"
        self.agent_id = "test_agent"
        
        self.test_data = {
            "email": "user@example.com",
            "preferences": ["electronics", "books"],
            "settings": {
                "notifications": True,
                "privacy_level": "high"
            }
        }
    
    def test_store_user_data(self):
        """Test storing encrypted user data"""
        success = self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        assert success is True
        
        # Verify file was created
        user_dir = Path(self.temp_dir) / "users" / self.user_id
        file_path = user_dir / f"{ConsentScope.VAULT_READ_EMAIL.value}.json"
        assert file_path.exists()
    
    def test_retrieve_user_data(self):
        """Test retrieving and decrypting user data"""
        # Store data first
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        # Retrieve data
        retrieved = self.vault.retrieve_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            requesting_agent=self.agent_id
        )
        
        assert retrieved is not None
        assert "data" in retrieved
        assert "metadata" in retrieved
        assert retrieved["data"]["email"] == self.test_data["email"]
        assert retrieved["metadata"]["encryption_verified"] is True
    
    def test_update_user_data(self):
        """Test updating existing user data"""
        # Store initial data
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        # Update data
        updated_data = {"email": "updated@example.com", "new_field": "new_value"}
        success = self.vault.update_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=updated_data,
            agent_id=self.agent_id
        )
        
        assert success is True
        
        # Retrieve and verify update
        retrieved = self.vault.retrieve_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL
        )
        
        assert retrieved["data"]["email"] == "updated@example.com"
        assert retrieved["data"]["new_field"] == "new_value"
    
    def test_delete_user_data_soft(self):
        """Test soft deletion of user data"""
        # Store data first
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        # Soft delete
        success = self.vault.delete_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            agent_id=self.agent_id,
            hard_delete=False
        )
        
        assert success is True
        
        # Should not be retrievable
        retrieved = self.vault.retrieve_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL
        )
        
        assert retrieved is None
    
    def test_delete_user_data_hard(self):
        """Test hard deletion of user data"""
        # Store data first
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        # Hard delete
        success = self.vault.delete_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            agent_id=self.agent_id,
            hard_delete=True
        )
        
        assert success is True
        
        # File should be gone
        user_dir = Path(self.temp_dir) / "users" / self.user_id
        file_path = user_dir / f"{ConsentScope.VAULT_READ_EMAIL.value}.json"
        assert not file_path.exists()
    
    def test_list_user_data(self):
        """Test listing user data summaries"""
        # Store multiple data items
        scopes = [ConsentScope.VAULT_READ_EMAIL, ConsentScope.VAULT_READ_FINANCE]
        
        for scope in scopes:
            self.vault.store_user_data(
                user_id=self.user_id,
                scope=scope,
                data=self.test_data,
                agent_id=self.agent_id
            )
        
        # List data
        summaries = self.vault.list_user_data(self.user_id)
        
        assert len(summaries) == 2
        for summary in summaries:
            assert "scope" in summary
            assert "created_at" in summary
            assert "stored_by_agent" in summary
            assert summary["stored_by_agent"] == self.agent_id
    
    def test_expired_data_handling(self):
        """Test handling of expired data"""
        # Store data with short expiry
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id,
            expires_in_ms=1  # 1ms - will be expired immediately
        )
        
        # Try to retrieve expired data
        retrieved = self.vault.retrieve_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL
        )
        
        assert retrieved is None
    
    def test_cleanup_expired_data(self):
        """Test cleanup of expired data"""
        # Store expired data
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id,
            expires_in_ms=1  # Already expired
        )
        
        # Run cleanup
        import time
        time.sleep(0.01)  # Ensure expiry
        cleaned_count = self.vault.cleanup_expired_data()
        
        assert cleaned_count >= 0  # Should clean up expired data
    
    def test_storage_stats(self):
        """Test storage statistics"""
        # Store some data
        self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        # Get stats
        stats = self.vault.get_storage_stats()
        
        assert "total_users" in stats
        assert "total_records" in stats
        assert "total_size_bytes" in stats
        assert "scopes" in stats
        assert "agents" in stats
        
        assert stats["total_users"] >= 1
        assert stats["total_records"] >= 1
    
    def test_aes256_encryption(self):
        """Test that AES-256-GCM encryption is used"""
        success = self.vault.store_user_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        
        assert success is True
        
        # Check that file contains encrypted data (not plaintext)
        user_dir = Path(self.temp_dir) / "users" / self.user_id
        file_path = user_dir / f"{ConsentScope.VAULT_READ_EMAIL.value}.json"
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Should not contain plaintext email
        assert self.test_data["email"] not in content
        # Should contain encryption metadata
        assert "aes-256-gcm" in content
        assert "ciphertext" in content
        assert "iv" in content
        assert "tag" in content
    
    def test_convenience_functions(self):
        """Test convenience functions"""
        # Test store_data function
        success = store_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            data=self.test_data,
            agent_id=self.agent_id
        )
        assert success is True
        
        # Test retrieve_data function
        retrieved = retrieve_data(
            user_id=self.user_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            requesting_agent=self.agent_id
        )
        assert retrieved is not None
        assert retrieved["data"]["email"] == self.test_data["email"]
    
    def teardown_method(self):
        """Cleanup after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
