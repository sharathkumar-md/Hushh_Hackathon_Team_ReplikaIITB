# hushh_mcp/vault/storage.py
"""
Enhanced Vault Storage System with AES-256-GCM encryption.

This implements a production-ready encrypted storage system for user data
following the "Best/Working/Winning Model" principles.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data, EncryptedPayload
from hushh_mcp.types import UserID, AgentID, VaultRecord, VaultKey
from hushh_mcp.constants import ConsentScope
from hushh_mcp.config import VAULT_ENCRYPTION_KEY

logger = logging.getLogger(__name__)

class VaultStorage:
    """
    Secure vault storage system with AES-256-GCM encryption.
    
    Best Model: Production-grade encryption and data integrity
    Working Model: Robust error handling and data validation
    Winning Model: User-centric data control and transparency
    """
    
    def __init__(self, vault_directory: str = "vault_data"):
        self.vault_dir = Path(vault_directory)
        self.vault_dir.mkdir(exist_ok=True)
        self.encryption_key = VAULT_ENCRYPTION_KEY
        
        # Create user subdirectories
        self.users_dir = self.vault_dir / "users"
        self.users_dir.mkdir(exist_ok=True)
        
        logger.info(f"🗄️ Vault storage initialized: {self.vault_dir.absolute()}")
    
    def store_user_data(
        self,
        user_id: UserID,
        scope: ConsentScope,
        data: Dict[str, Any],
        agent_id: AgentID,
        expires_in_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store encrypted user data in vault.
        
        Args:
            user_id: User identifier
            scope: Data scope (email, finance, etc.)
            data: Data to encrypt and store
            agent_id: Agent storing the data
            expires_in_ms: Optional expiration time
            metadata: Optional metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Create user directory
            user_dir = self.users_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Encrypt the data
            encrypted_payload = encrypt_data(
                plaintext=json.dumps(data, default=str),
                key_hex=self.encryption_key
            )
            
            # Create vault record
            current_time = int(time.time() * 1000)
            vault_key = VaultKey(user_id=user_id, scope=scope)
            vault_record = VaultRecord(
                key=vault_key,
                data=encrypted_payload,
                agent_id=agent_id,
                created_at=current_time,
                updated_at=current_time,
                expires_at=current_time + expires_in_ms if expires_in_ms else None,
                metadata=metadata or {}
            )
            
            # Store to file
            file_path = user_dir / f"{scope.value}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(vault_record.dict(), f, indent=2)
            
            logger.info(f"🔐 Data stored for {user_id} in scope {scope.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store vault data: {str(e)}", exc_info=True)
            return False
    
    def retrieve_user_data(
        self,
        user_id: UserID,
        scope: ConsentScope,
        requesting_agent: Optional[AgentID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt user data from vault.
        
        Args:
            user_id: User identifier
            scope: Data scope to retrieve
            requesting_agent: Agent requesting the data
            
        Returns:
            Dict containing decrypted data or None if not found/expired
        """
        try:
            file_path = self.users_dir / user_id / f"{scope.value}.json"
            
            if not file_path.exists():
                logger.warning(f"No data found for {user_id} in scope {scope.value}")
                return None
            
            # Load vault record
            with open(file_path, 'r', encoding='utf-8') as f:
                record_data = json.load(f)
            
            vault_record = VaultRecord(**record_data)
            
            # Check expiration
            current_time = int(time.time() * 1000)
            if vault_record.expires_at and current_time > vault_record.expires_at:
                logger.warning(f"Data expired for {user_id} in scope {scope.value}")
                return None
            
            # Check if deleted
            if vault_record.deleted:
                logger.warning(f"Data marked as deleted for {user_id} in scope {scope.value}")
                return None
            
            # Decrypt data
            decrypted_text = decrypt_data(vault_record.data, self.encryption_key)
            decrypted_data = json.loads(decrypted_text)
            
            # Add metadata for transparency
            result = {
                "data": decrypted_data,
                "metadata": {
                    "created_at": vault_record.created_at,
                    "updated_at": vault_record.updated_at,
                    "expires_at": vault_record.expires_at,
                    "stored_by_agent": vault_record.agent_id,
                    "requesting_agent": requesting_agent,
                    "scope": scope.value,
                    "encryption_verified": True
                }
            }
            
            logger.info(f"🔓 Data retrieved for {user_id} in scope {scope.value}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve vault data: {str(e)}", exc_info=True)
            return None
    
    def update_user_data(
        self,
        user_id: UserID,
        scope: ConsentScope,
        data: Dict[str, Any],
        agent_id: AgentID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing user data in vault.
        """
        try:
            file_path = self.users_dir / user_id / f"{scope.value}.json"
            
            if not file_path.exists():
                logger.warning(f"No existing data to update for {user_id} in scope {scope.value}")
                return False
            
            # Load existing record
            with open(file_path, 'r', encoding='utf-8') as f:
                record_data = json.load(f)
            
            vault_record = VaultRecord(**record_data)
            
            # Encrypt new data
            encrypted_payload = encrypt_data(
                plaintext=json.dumps(data, default=str),
                key_hex=self.encryption_key
            )
            
            # Update record
            vault_record.data = encrypted_payload
            vault_record.updated_at = int(time.time() * 1000)
            vault_record.agent_id = agent_id  # Track who updated it
            if metadata:
                vault_record.metadata.update(metadata)
            
            # Save updated record
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(vault_record.dict(), f, indent=2)
            
            logger.info(f"📝 Data updated for {user_id} in scope {scope.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update vault data: {str(e)}", exc_info=True)
            return False
    
    def delete_user_data(
        self,
        user_id: UserID,
        scope: ConsentScope,
        agent_id: AgentID,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete user data from vault.
        
        Args:
            user_id: User identifier
            scope: Data scope to delete
            agent_id: Agent requesting deletion
            hard_delete: If True, physically remove file. If False, mark as deleted.
            
        Returns:
            bool: Success status
        """
        try:
            file_path = self.users_dir / user_id / f"{scope.value}.json"
            
            if not file_path.exists():
                logger.warning(f"No data to delete for {user_id} in scope {scope.value}")
                return False
            
            if hard_delete:
                # Physical deletion
                file_path.unlink()
                logger.info(f"🗑️ Data hard deleted for {user_id} in scope {scope.value}")
            else:
                # Soft deletion - mark as deleted
                with open(file_path, 'r', encoding='utf-8') as f:
                    record_data = json.load(f)
                
                vault_record = VaultRecord(**record_data)
                vault_record.deleted = True
                vault_record.updated_at = int(time.time() * 1000)
                vault_record.metadata["deleted_by"] = agent_id
                vault_record.metadata["deletion_timestamp"] = vault_record.updated_at
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(vault_record.dict(), f, indent=2)
                
                logger.info(f"🗑️ Data soft deleted for {user_id} in scope {scope.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vault data: {str(e)}", exc_info=True)
            return False
    
    def list_user_data(self, user_id: UserID) -> List[Dict[str, Any]]:
        """
        List all data stored for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of data summaries (no actual content for security)
        """
        try:
            user_dir = self.users_dir / user_id
            
            if not user_dir.exists():
                return []
            
            summaries = []
            for file_path in user_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        record_data = json.load(f)
                    
                    vault_record = VaultRecord(**record_data)
                    
                    # Don't include actual data for security
                    summary = {
                        "scope": vault_record.key.scope,
                        "created_at": vault_record.created_at,
                        "updated_at": vault_record.updated_at,
                        "expires_at": vault_record.expires_at,
                        "stored_by_agent": vault_record.agent_id,
                        "deleted": vault_record.deleted,
                        "metadata": vault_record.metadata,
                        "file_size_bytes": file_path.stat().st_size
                    }
                    summaries.append(summary)
                    
                except Exception as e:
                    logger.warning(f"Failed to read vault file {file_path}: {str(e)}")
                    continue
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to list user data: {str(e)}", exc_info=True)
            return []
    
    def cleanup_expired_data(self) -> int:
        """
        Clean up expired data from vault.
        
        Returns:
            int: Number of expired records cleaned up
        """
        cleaned_count = 0
        current_time = int(time.time() * 1000)
        
        try:
            for user_dir in self.users_dir.iterdir():
                if not user_dir.is_dir():
                    continue
                
                for file_path in user_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            record_data = json.load(f)
                        
                        vault_record = VaultRecord(**record_data)
                        
                        if vault_record.expires_at and current_time > vault_record.expires_at:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.info(f"🧹 Cleaned expired data: {file_path}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to check expiry for {file_path}: {str(e)}")
                        continue
            
            logger.info(f"🧹 Cleanup completed: {cleaned_count} expired records removed")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {str(e)}", exc_info=True)
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get vault storage statistics.
        
        Returns:
            Dict with storage statistics
        """
        try:
            stats = {
                "total_users": 0,
                "total_records": 0,
                "total_size_bytes": 0,
                "scopes": {},
                "agents": {},
                "expired_records": 0,
                "deleted_records": 0
            }
            
            current_time = int(time.time() * 1000)
            
            for user_dir in self.users_dir.iterdir():
                if not user_dir.is_dir():
                    continue
                
                stats["total_users"] += 1
                
                for file_path in user_dir.glob("*.json"):
                    try:
                        stats["total_records"] += 1
                        stats["total_size_bytes"] += file_path.stat().st_size
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            record_data = json.load(f)
                        
                        vault_record = VaultRecord(**record_data)
                        
                        # Count by scope
                        scope = vault_record.key.scope
                        stats["scopes"][scope] = stats["scopes"].get(scope, 0) + 1
                        
                        # Count by agent
                        agent = vault_record.agent_id
                        stats["agents"][agent] = stats["agents"].get(agent, 0) + 1
                        
                        # Count expired
                        if vault_record.expires_at and current_time > vault_record.expires_at:
                            stats["expired_records"] += 1
                        
                        # Count deleted
                        if vault_record.deleted:
                            stats["deleted_records"] += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to read stats for {file_path}: {str(e)}")
                        continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}", exc_info=True)
            return {"error": str(e)}

# Global vault storage instance
vault_storage = VaultStorage()

# Convenience functions for agents to use
def store_data(user_id: UserID, scope: ConsentScope, data: Dict[str, Any], agent_id: AgentID, **kwargs) -> bool:
    """Store data in vault with encryption"""
    return vault_storage.store_user_data(user_id, scope, data, agent_id, **kwargs)

def retrieve_data(user_id: UserID, scope: ConsentScope, requesting_agent: Optional[AgentID] = None) -> Optional[Dict[str, Any]]:
    """Retrieve and decrypt data from vault"""
    return vault_storage.retrieve_user_data(user_id, scope, requesting_agent)

def update_data(user_id: UserID, scope: ConsentScope, data: Dict[str, Any], agent_id: AgentID, **kwargs) -> bool:
    """Update existing data in vault"""
    return vault_storage.update_user_data(user_id, scope, data, agent_id, **kwargs)

def delete_data(user_id: UserID, scope: ConsentScope, agent_id: AgentID, hard_delete: bool = False) -> bool:
    """Delete data from vault"""
    return vault_storage.delete_user_data(user_id, scope, agent_id, hard_delete)

if __name__ == "__main__":
    # Test the vault storage
    print("🧪 Testing Vault Storage...")
    
    # Store test data
    test_data = {
        "email": "user@example.com",
        "preferences": ["electronics", "books"],
        "last_login": "2025-07-24T12:00:00Z"
    }
    
    success = store_data(
        user_id="test_user",
        scope=ConsentScope.VAULT_READ_EMAIL,
        data=test_data,
        agent_id="test_agent"
    )
    print(f"✅ Store success: {success}")
    
    # Retrieve test data
    retrieved = retrieve_data(
        user_id="test_user",
        scope=ConsentScope.VAULT_READ_EMAIL,
        requesting_agent="test_agent"
    )
    print(f"✅ Retrieved data: {retrieved is not None}")
    
    # Get stats
    stats = vault_storage.get_storage_stats()
    print(f"📊 Storage stats: {stats}")
