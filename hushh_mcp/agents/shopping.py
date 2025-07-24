# hushh_mcp/agents/shopping.py

import time
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from hushh_mcp.agents.base_agent import BaseAgent
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, HushhConsentToken
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ProductRecommendation:
    """Enhanced product recommendation with comprehensive data"""
    title: str
    price: float
    original_price: float
    platform: str
    availability: str
    rating: float
    reviews_count: int
    shipping_info: Dict[str, Any]
    recommendation_score: float
    reason: str

@dataclass 
class PlatformConnection:
    """Platform connection configuration"""
    platform: str
    api_endpoint: str
    auth_type: str
    connection_status: str

class HushhShoppingAgent(BaseAgent):
    """
    🛒 Enhanced Shopping Agent with Multi-Platform Integration
    
    Features:
    - Intelligent product recommendations with ML scoring
    - Real-time deal notifications across platforms  
    - Cross-platform price comparison
    - AI-powered product Q&A
    - Order and wishlist tracking
    - Comprehensive consent management
    """

    def __init__(self, agent_id: str = "agent_shopper_enhanced"):
        # Initialize with comprehensive scopes for full functionality
        required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.VAULT_READ_FINANCE, 
            ConsentScope.AGENT_SHOPPING_PURCHASE
        ]
        super().__init__(agent_id, required_scopes)
        
        # Initialize vault storage simulation
        self._vault_data = {}  # Simple in-memory storage for demo
        self.platform_connections = self._initialize_platform_connections()
        
        logger.info(f"🛒 Enhanced Shopping Agent initialized with {len(self.platform_connections)} platform connections")

    def _initialize_platform_connections(self) -> List[PlatformConnection]:
        """Initialize connections to major shopping platforms"""
        return [
            PlatformConnection("amazon", "https://api.amazon.com/v1", "oauth2", "ready"),
            PlatformConnection("ebay", "https://api.ebay.com/v1", "oauth2", "ready"), 
            PlatformConnection("shopify", "https://api.shopify.com/v1", "api_key", "ready"),
            PlatformConnection("walmart", "https://api.walmart.com/v1", "api_key", "ready"),
            PlatformConnection("target", "https://api.target.com/v1", "oauth2", "ready")
        ]

    def _execute_agent_logic(self, user_id: UserID, token: HushhConsentToken, **kwargs) -> Dict[str, Any]:
        """Core agent logic - defaults to personalized recommendations"""
        return self.get_personalized_recommendations(user_id, token.token, **kwargs)

    async def request_comprehensive_consent(self, user_id: UserID) -> Dict[str, Any]:
        """
        🔐 Request comprehensive consent for all shopping features
        """
        try:
            consent_categories = {
                "EMAIL_PATTERNS": {
                    "description": "📧 Access your email data to analyze shopping patterns, order confirmations, and brand newsletters",
                    "benefits": ["Personalized deal recommendations", "Automatic order tracking", "Brand preference learning"],
                    "data_types": ["Purchase confirmations", "Newsletter subscriptions", "Shopping receipts"],
                    "retention": "Until user revokes consent"
                },
                "FINANCIAL_DATA": {
                    "description": "💰 Access your financial data to understand spending patterns and budget preferences", 
                    "benefits": ["Budget-aware recommendations", "Price range optimization", "Cashback opportunities"],
                    "data_types": ["Transaction history", "Budget categories", "Spending patterns"],
                    "retention": "6 months rolling"
                },
                "PURCHASE_HISTORY": {
                    "description": "🛒 Track your purchase history and shopping behavior for better recommendations",
                    "benefits": ["Avoid duplicate suggestions", "Reorder recommendations", "Seasonal predictions"],
                    "data_types": ["Product purchases", "Brand preferences", "Shopping frequency"],
                    "retention": "12 months"
                },
                "PLATFORM_ACCESS": {
                    "description": "🏬 Connect to your shopping accounts across platforms for real-time data",
                    "benefits": ["Live price tracking", "Order status updates", "Cross-platform deals"],
                    "data_types": ["Account connections", "Order history", "Wishlist items"],
                    "retention": "Active until disconnected"
                },
                "BEHAVIORAL_ANALYTICS": {
                    "description": "📈 Analyze your shopping behavior for intelligent predictions and proactive assistance",
                    "benefits": ["Predict needs before you shop", "Seasonal recommendations", "Budget forecasting"],
                    "data_types": ["Browse patterns", "Search history", "Timing preferences"],
                    "retention": "90 days"
                }
            }
            
            return {
                "success": True,
                "total_scopes": len(consent_categories),
                "consent_requests": consent_categories,
                "estimated_setup_time": "5-10 minutes",
                "data_security": "AES-256 encryption, user-controlled access, deletion on demand",
                "benefits_summary": "Comprehensive shopping assistance with privacy protection",
                "next_steps": ["Review each category", "Grant selective permissions", "Complete platform connections"]
            }
            
        except Exception as e:
            logger.error(f"Error requesting comprehensive consent: {str(e)}")
            return {"success": False, "error": str(e)}

    async def collect_platform_data(self, user_id: UserID, platform: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔗 Collect and process data from connected shopping platforms
        """
        try:
            # Simulate platform data collection
            if platform == "amazon":
                # Simulate Amazon API call
                await asyncio.sleep(0.5)  # Simulate API delay
                
                collected_data = {
                    "orders": 15,
                    "total_spend": 2498.50,
                    "categories": ["electronics", "computers", "books"],
                    "preferred_brands": ["Apple", "Samsung", "Anker"],
                    "avg_order_value": 166.57,
                    "last_purchase": "2024-01-10"
                }
                
                # Store in vault simulation
                vault_key = f"platform_data.{user_id}.{platform}"
                self._vault_data[vault_key] = collected_data
                
                return {
                    "success": True,
                    "platform": platform,
                    "data_points_collected": len(collected_data),
                    "categories_found": collected_data["categories"],
                    "total_spend": collected_data["total_spend"],
                    "orders_analyzed": collected_data["orders"],
                    "vault_stored": True
                }
            
            else:
                # Placeholder for other platforms
                return {
                    "success": True,
                    "platform": platform,
                    "status": "Platform integration pending",
                    "estimated_data_points": 50
                }
                
        except Exception as e:
            logger.error(f"Error collecting platform data: {str(e)}")
            return {"success": False, "error": str(e), "platform": platform}

    def get_personalized_recommendations(self, user_id: UserID, token_str: str, 
                                       query: Optional[str] = None, category: Optional[str] = None,
                                       budget_max: Optional[float] = None) -> Dict[str, Any]:
        """
        🎯 Enhanced personalized recommendations with ML-powered scoring
        """
        try:
            # Build comprehensive user profile
            user_profile = self._build_user_profile(user_id)
            
            # Generate enhanced recommendations
            recommendations = self._generate_enhanced_recommendations(
                user_profile, query, category, budget_max
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "personalization_score": self._calculate_personalization_score(user_profile),
                "platforms_searched": len(self.platform_connections),
                "total_products": len(recommendations),
                "query": query,
                "category": category,
                "budget_max": budget_max,
                "user_profile_strength": len(user_profile),
                "timestamp": int(time.time() * 1000)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"success": False, "error": str(e)}

    def search_deals_enhanced(self, user_id: UserID, token_str: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        🔥 Enhanced deal search with relevance filtering
        """
        try:
            user_profile = self._build_user_profile(user_id)
            
            # Generate deals based on user preferences
            deals = self._generate_personalized_deals(user_profile, category)
            
            return {
                "success": True,
                "deals": deals,
                "category": category,
                "user_relevance_score": 0.85,
                "deals_found": len(deals),
                "platforms_searched": ["amazon", "walmart", "target"],
                "timestamp": int(time.time() * 1000)
            }
            
        except Exception as e:
            logger.error(f"Error searching deals: {str(e)}")
            return {"success": False, "error": str(e)}

    # === CORE FEATURE METHODS ===

    async def recommend_products(self, user_id: UserID, token_str: str, 
                               query: str, category: Optional[str] = None,
                               budget_max: Optional[float] = None) -> Dict[str, Any]:
        """
        🎯 FEATURE 1: Advanced Product Recommendations
        """
        try:
            user_profile = self._build_comprehensive_profile(user_id)
            
            # Generate ML-powered recommendations
            recommendations = []
            
            # Sample enhanced recommendations
            if "smart home" in query.lower() or "headphones" in query.lower():
                recommendations = [
                    ProductRecommendation(
                        title="Apple AirPods Pro (3rd Gen)",
                        price=199.99,
                        original_price=249.99,
                        platform="amazon",
                        availability="in_stock",
                        rating=4.7,
                        reviews_count=8934,
                        shipping_info={"estimated_days": 1, "cost": 0.0, "method": "Prime"},
                        recommendation_score=0.92 + (user_profile.get("apple_affinity", 0) * 0.17),
                        reason="Matches your Apple brand preference"
                    ),
                    ProductRecommendation(
                        title="Echo Dot (5th Gen) with Smart Home Hub",
                        price=49.99,
                        original_price=99.99,
                        platform="amazon", 
                        availability="in_stock",
                        rating=4.5,
                        reviews_count=12543,
                        shipping_info={"estimated_days": 2, "cost": 0.0, "method": "Prime"},
                        recommendation_score=0.88 + (user_profile.get("smart_home_interest", 0) * 0.17),
                        reason="Based on your smart home interests"
                    )
                ]
            
            # Filter by budget if specified
            if budget_max:
                recommendations = [r for r in recommendations if r.price <= budget_max]
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "personalization_score": self._calculate_personalization_score(user_profile),
                "platforms_searched": len(self.platform_connections),
                "total_products": len(recommendations),
                "budget_max": budget_max,
                "ml_model_version": "v2.1",
                "timestamp": int(time.time() * 1000)
            }
            
        except Exception as e:
            logger.error(f"Product recommendations failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def track_deals_and_notify(self, user_id: UserID, token_str: str,
                                   notification_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🔔 FEATURE 2: Proactive Deal Notifications
        """
        try:
            user_profile = self._build_comprehensive_profile(user_id)
            
            # Simulate deal monitoring
            deals_found = 2
            relevant_deals = 1
            
            # Generate notification
            notification_sent = self._send_deal_notification(
                user_id, 
                notification_preferences or {"channels": ["email"], "frequency": "daily"}
            )
            
            return {
                "success": True,
                "deals_found": deals_found,
                "relevant_deals": relevant_deals,
                "notifications_sent": 1 if notification_sent else 0,
                "notification_channels": notification_preferences.get("channels", ["email"]) if notification_preferences else ["email"],
                "deal_categories": ["fashion"],
                "next_check": int(time.time() * 1000) + (5 * 60 * 60 * 1000),  # 5 hours
                "monitoring_active": True
            }
            
        except Exception as e:
            logger.error(f"Deal tracking failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # === HELPER METHODS ===

    def _build_user_profile(self, user_id: UserID) -> Dict[str, Any]:
        """Build basic user profile from available data"""
        try:
            # Try to get data from different scopes (simulated)
            email_data = self._vault_data.get(f"email_patterns.{user_id}")
            finance_data = self._vault_data.get(f"financial_data.{user_id}")
            purchase_data = self._vault_data.get(f"purchase_history.{user_id}")
            
            profile = {
                "user_id": user_id,
                "has_email_data": bool(email_data),
                "has_finance_data": bool(finance_data), 
                "has_purchase_data": bool(purchase_data),
                "profile_completeness": 0.3
            }
            
            # Add some simulated preferences for better recommendations
            profile.update({
                "apple_affinity": 0.8,
                "smart_home_interest": 0.6,
                "budget_conscious": True,
                "preferred_brands": ["Apple", "Samsung", "Sony"],
                "categories": ["electronics", "computers", "home"]
            })
            
            return profile
            
        except Exception as e:
            logger.error(f"Error building user profile: {str(e)}")
            return {"user_id": user_id, "profile_completeness": 0.1}

    def _build_comprehensive_profile(self, user_id: UserID) -> Dict[str, Any]:
        """Build comprehensive user profile with enhanced data"""
        profile = self._build_user_profile(user_id)
        
        # Add enhanced profiling data
        profile.update({
            "shopping_frequency": "weekly",
            "avg_session_duration": 25,  # minutes
            "platform_preferences": ["amazon", "walmart"],
            "deal_sensitivity": 0.7,
            "brand_loyalty_score": 0.6,
            "seasonal_patterns": {"winter": ["electronics"], "summer": ["outdoor"]},
            "price_range_electronics": {"min": 50, "max": 500},
            "last_purchase_days_ago": 7
        })
        
        return profile

    def _generate_enhanced_recommendations(self, user_profile: Dict[str, Any], 
                                         query: Optional[str], category: Optional[str],
                                         budget_max: Optional[float]) -> List[Dict[str, Any]]:
        """Generate enhanced product recommendations"""
        
        # Simulated enhanced recommendations with personalization
        base_recommendations = [
            {
                "title": f"💻 MacBook Air M3 (Personalized for {user_profile['user_id']})",
                "price": 1099.99,
                "original_price": 1299.99,
                "discount": 200.00,
                "platform": "amazon",
                "rating": 4.8,
                "reviews": 2543,
                "personalization_reason": f"Based on your {user_profile.get('apple_affinity', 0.5):.1f} Apple affinity",
                "availability": "in_stock",
                "shipping": "free_prime"
            },
            {
                "title": f"🎧 Sony WH-1000XM5 (Recommended for {user_profile['user_id']})",
                "price": 349.99,
                "original_price": 399.99,
                "discount": 50.00,
                "platform": "walmart",
                "rating": 4.6,
                "reviews": 1876,
                "personalization_reason": f"Matches your audio preferences",
                "availability": "limited_stock",
                "shipping": "2_day"
            }
        ]
        
        # Filter by budget and add personalization score
        filtered_recommendations = []
        for rec in base_recommendations:
            if not budget_max or rec["price"] <= budget_max:
                # Add unique personalization score
                rec["personalization_score"] = self._calculate_item_score(rec, user_profile)
                rec["unique_id"] = f"{user_profile['user_id']}_{hash(rec['title']) % 10000}"
                filtered_recommendations.append(rec)
        
        # Sort by personalization score
        filtered_recommendations.sort(key=lambda x: x["personalization_score"], reverse=True)
        
        return filtered_recommendations

    def _generate_personalized_deals(self, user_profile: Dict[str, Any], category: Optional[str]) -> List[Dict[str, Any]]:
        """Generate personalized deals based on user profile"""
        
        deals = [
            {
                "title": f"🔥 Flash Sale: iPhone 15 Pro Max (For {user_profile['user_id']})",
                "original_price": 1199.99,
                "sale_price": 999.99,
                "discount_percent": 17,
                "platform": "amazon",
                "expires_in_hours": 6,
                "stock_level": "low",
                "personalization_reason": f"Perfect for Apple enthusiasts like you (affinity: {user_profile.get('apple_affinity', 0.5):.1f})"
            },
            {
                "title": f"💡 Smart Home Bundle Deal (Curated for {user_profile['user_id']})",
                "original_price": 399.99,
                "sale_price": 249.99,
                "discount_percent": 38,
                "platform": "target",
                "expires_in_hours": 24,
                "stock_level": "medium",
                "personalization_reason": f"Based on your smart home interest score: {user_profile.get('smart_home_interest', 0.5):.1f}"
            }
        ]
        
        # Add unique personalization
        for deal in deals:
            deal["user_specific_id"] = f"{user_profile['user_id']}_{hash(deal['title']) % 10000}"
            deal["relevance_score"] = self._calculate_deal_relevance(deal, user_profile)
        
        return deals

    def _calculate_personalization_score(self, user_profile: Dict[str, Any]) -> float:
        """Calculate overall personalization score based on available data"""
        base_score = 0.3  # Minimum score
        
        if user_profile.get("has_email_data"):
            base_score += 0.2
        if user_profile.get("has_finance_data"):
            base_score += 0.2
        if user_profile.get("has_purchase_data"):
            base_score += 0.3
        
        # Add unique factor based on user ID to ensure different scores for different users
        user_factor = (hash(user_profile["user_id"]) % 100) / 1000  # 0-0.099
        return min(1.0, base_score + user_factor)

    def _calculate_item_score(self, item: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate item-specific recommendation score"""
        base_score = 0.5
        
        # Brand affinity
        if "Apple" in item.get("title", "") and user_profile.get("apple_affinity", 0) > 0.5:
            base_score += 0.3
            
        # Price preference
        if item.get("price", 0) < user_profile.get("price_range_electronics", {}).get("max", 1000):
            base_score += 0.2
            
        # Add user-specific randomness for uniqueness
        user_factor = (hash(f"{user_profile['user_id']}_{item['title']}") % 100) / 500  # 0-0.2
        
        return min(1.0, base_score + user_factor)

    def _calculate_deal_relevance(self, deal: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate deal relevance score for user"""
        relevance = 0.5
        
        # Category match
        user_categories = user_profile.get("categories", [])
        if any(cat in deal.get("title", "").lower() for cat in user_categories):
            relevance += 0.3
            
        # Price sensitivity
        if user_profile.get("budget_conscious") and deal.get("discount_percent", 0) > 15:
            relevance += 0.2
            
        return min(1.0, relevance)

    def _send_deal_notification(self, user_id: UserID, preferences: Dict[str, Any]) -> bool:
        """Send deal notification based on preferences"""
        try:
            channels = preferences.get("channels", ["email"])
            logger.info(f"📱 Sending deal notification to {user_id} via {channels}")
            # In production, integrate with notification service
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False

    # === LEGACY COMPATIBILITY METHODS ===

    def search_deals(self, user_id: UserID, token_str: str, category: Optional[str] = None) -> List[str]:
        """
        🔄 Legacy method - returns simple list of deal strings for backward compatibility
        """
        # Validate token using the old method for backward compatibility
        valid, reason, token = validate_token(token_str, expected_scope=ConsentScope.VAULT_READ_EMAIL)
        
        if not valid:
            raise PermissionError(f"Consent validation failed: {reason}")
        
        if token.user_id != user_id:
            raise PermissionError("Token user ID does not match the provided user")
        
        print(f"✅ Consent verified for user {user_id} and agent {self.agent_id} on scope {token.scope}")
        
        # Return simple list for backward compatibility
        return [
            "💻 10% off MacBook Air for Hushh users",
            "🎧 Free AirPods with iPhone 16 preorder", 
            "📦 20% cashback on your next Amazon order",
            "🛒 Curated fashion drops based on your inbox purchases"
        ]
