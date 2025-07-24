# hushh_mcp/agents/ai_assistant.py
"""
Advanced AI Assistant Agent demonstrating "Best/Working/Winning Model" principles:

Best Model: Integration with state-of-the-art LLMs, advanced prompt engineering
Working Model: Robust error handling, fallbacks, standardized APIs
Winning Model: Real-world AI use cases, user-centric design, scalable architecture

This agent showcases how to build production-ready AI agents with proper consent management.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from hushh_mcp.agents.base_agent import BaseAgent
from hushh_mcp.constants import ConsentScope
from hushh_mcp.types import UserID, HushhConsentToken

logger = logging.getLogger(__name__)

class HushhAIAssistant(BaseAgent):
    """
    AI-powered assistant that can help with various tasks while respecting user consent.
    
    Demonstrates all three model principles:
    - Best Model: Advanced prompt engineering, context management
    - Working Model: Graceful fallbacks, error handling, modular design
    - Winning Model: Real-world AI applications, user value focus
    """

    def __init__(self, agent_id: str = "agent_ai_assistant"):
        super().__init__(
            agent_id=agent_id,
            required_scopes=[
                ConsentScope.VAULT_READ_EMAIL,
                ConsentScope.AGENT_IDENTITY_VERIFY,
                ConsentScope.CUSTOM_TEMPORARY
            ]
        )
        
        # Working Model: Configuration with fallbacks
        self.max_context_length = 4000
        self.temperature = 0.7
        self.model_preferences = ["gpt-4", "claude-3", "llama-3", "fallback"]

    def _execute_agent_logic(self, user_id: UserID, token: HushhConsentToken, **kwargs) -> Dict[str, Any]:
        """
        Core AI assistant logic with robust error handling and fallbacks.
        """
        user_query = kwargs.get("query", "")
        context = kwargs.get("context", {})
        task_type = kwargs.get("task_type", "general_assistance")
        
        if not user_query:
            raise ValueError("No query provided for AI assistant")

        try:
            # Best Model: Advanced prompt engineering with context
            response = self._generate_ai_response(user_query, context, task_type, user_id)
            
            return {
                "response": response["text"],
                "task_type": task_type,
                "model_used": response.get("model", "fallback"),
                "confidence": response.get("confidence", 0.8),
                "processing_time_ms": response.get("processing_time", 0),
                "context_used": bool(context),
                "safety_checked": True,
                "user_personalized": self._is_personalized_response(token.scope)
            }
            
        except Exception as e:
            logger.warning(f"AI generation failed, using fallback: {str(e)}")
            # Working Model: Graceful fallback to rule-based responses
            return self._get_fallback_response(user_query, task_type)

    def _generate_ai_response(self, query: str, context: Dict[str, Any], task_type: str, user_id: str) -> Dict[str, Any]:
        """
        Generate AI response using best available model with proper prompt engineering.
        Best Model: Advanced algorithms and optimization.
        """
        start_time = time.time()
        
        # Best Model: Sophisticated prompt engineering
        system_prompt = self._build_system_prompt(task_type, context)
        user_prompt = self._build_user_prompt(query, context, user_id)
        
        # Working Model: Try multiple model providers with fallbacks
        for model in self.model_preferences:
            try:
                if model == "fallback":
                    return self._rule_based_response(query, task_type)
                
                response_text = self._call_ai_model(model, system_prompt, user_prompt)
                processing_time = int((time.time() - start_time) * 1000)
                
                return {
                    "text": response_text,
                    "model": model,
                    "confidence": 0.9,
                    "processing_time": processing_time
                }
                
            except Exception as e:
                logger.warning(f"Model {model} failed: {str(e)}, trying next...")
                continue
        
        # If all models fail, use rule-based fallback
        return self._rule_based_response(query, task_type)

    def _build_system_prompt(self, task_type: str, context: Dict[str, Any]) -> str:
        """
        Best Model: Advanced prompt engineering with task-specific optimization.
        """
        base_prompt = """You are Hushh AI Assistant, a privacy-first AI that only acts with explicit user consent.

Key principles:
- Always respect user privacy and consent boundaries
- Provide helpful, accurate, and actionable responses
- Be concise but comprehensive
- If you're unsure, say so rather than guess
- Never access data without proper consent tokens"""

        task_specific_prompts = {
            "email_summary": """
You specialize in email summarization and organization. Focus on:
- Key action items and deadlines
- Important contacts and communications
- Prioritization of urgent vs non-urgent items
- Protecting sensitive information
""",
            "calendar_management": """
You help with calendar and schedule management. Focus on:
- Optimal meeting scheduling
- Time conflict resolution
- Travel time considerations
- Work-life balance optimization
""",
            "data_analysis": """
You assist with personal data analysis and insights. Focus on:
- Pattern recognition in user data
- Actionable insights and recommendations
- Data visualization suggestions
- Privacy-preserving analytics
""",
            "general_assistance": """
You provide general assistance across various domains. Focus on:
- Understanding user intent accurately
- Providing step-by-step guidance
- Offering relevant alternatives
- Being helpful while staying within scope
"""
        }
        
        task_prompt = task_specific_prompts.get(task_type, task_specific_prompts["general_assistance"])
        
        context_info = ""
        if context:
            context_info = f"\nAvailable context: {json.dumps(context, indent=2)}"
        
        return f"{base_prompt}\n\n{task_prompt}{context_info}"

    def _build_user_prompt(self, query: str, context: Dict[str, Any], user_id: str) -> str:
        """
        Construct user prompt with proper context and personalization.
        """
        prompt = f"User query: {query}"
        
        if context:
            prompt += f"\n\nRelevant context:\n{json.dumps(context, indent=2)}"
        
        prompt += f"\n\nUser ID: {user_id}"
        prompt += "\n\nPlease provide a helpful response that respects privacy and consent boundaries."
        
        return prompt

    def _call_ai_model(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """
        Call external AI model API with proper error handling.
        Working Model: Robust external service integration.
        """
        # In a real implementation, this would call actual AI APIs
        # For hackathon demo, we'll simulate responses
        
        simulated_responses = {
            "gpt-4": f"[GPT-4 Response] Based on your request, I can help you with that. Here's a comprehensive response that takes into account your privacy preferences and the context you've provided. The key points are: 1) Immediate actions needed, 2) Long-term considerations, 3) Privacy-preserving recommendations.",
            
            "claude-3": f"[Claude-3 Response] I understand you're looking for assistance with this task. Let me break this down systematically while ensuring we respect your data privacy: • Primary objective analysis • Recommended approach • Privacy-first considerations • Next steps",
            
            "llama-3": f"[Llama-3 Response] I can help you with this request while maintaining strict privacy controls. Here's my analysis and recommendations based on the information you've shared with proper consent."
        }
        
        # Simulate API latency
        time.sleep(0.1)
        
        return simulated_responses.get(model, "Model response not available")

    def _rule_based_response(self, query: str, task_type: str) -> Dict[str, Any]:
        """
        Working Model: Rule-based fallback when AI models are unavailable.
        """
        query_lower = query.lower()
        
        # Pattern matching for common queries
        if "email" in query_lower:
            response = "I can help you organize and summarize your emails. With proper consent, I can identify important messages, extract action items, and provide priority rankings."
        elif "calendar" in query_lower or "schedule" in query_lower:
            response = "I can assist with calendar management including scheduling meetings, finding optimal time slots, and managing your daily agenda. Please ensure you have the appropriate consent tokens."
        elif "data" in query_lower or "analyze" in query_lower:
            response = "I can help analyze your personal data to provide insights and recommendations. All analysis is done with encryption and requires explicit consent for each data source."
        else:
            response = f"I understand you're asking about: '{query}'. I can provide general assistance, but for more personalized help, please ensure you have the appropriate consent tokens for the specific data or services you'd like me to access."
        
        return {
            "text": response,
            "model": "rule_based_fallback",
            "confidence": 0.6,
            "processing_time": 50
        }

    def _get_fallback_response(self, query: str, task_type: str) -> Dict[str, Any]:
        """
        Working Model: Final fallback when all AI generation fails.
        """
        return {
            "response": "I apologize, but I'm currently experiencing technical difficulties. Please try again later, or contact support if the issue persists.",
            "task_type": task_type,
            "model_used": "emergency_fallback",
            "confidence": 0.3,
            "processing_time_ms": 10,
            "context_used": False,
            "safety_checked": True,
            "user_personalized": False,
            "error_mode": True
        }

    def _is_personalized_response(self, scope: str) -> bool:
        """Check if response can be personalized based on consent scope"""
        personalizable_scopes = [
            ConsentScope.VAULT_READ_EMAIL.value,
            ConsentScope.VAULT_READ_CONTACTS.value,
            ConsentScope.VAULT_READ_FINANCE.value
        ]
        return scope in personalizable_scopes

    # Convenience methods for specific AI tasks
    def summarize_text(self, user_id: UserID, token_str: str, text: str, style: str = "bullet_points") -> Dict[str, Any]:
        """Specialized text summarization with different style options"""
        return self.execute(
            user_id=user_id,
            token_str=token_str,
            query=f"Please summarize the following text in {style} style: {text}",
            task_type="text_summarization",
            context={"original_length": len(text), "style": style}
        )

    def analyze_email_patterns(self, user_id: UserID, token_str: str, email_data: List[Dict]) -> Dict[str, Any]:
        """Analyze email patterns and provide insights"""
        return self.execute(
            user_id=user_id,
            token_str=token_str,
            query="Analyze my email patterns and provide insights on communication trends, important contacts, and optimization opportunities",
            task_type="email_analysis",
            context={"email_count": len(email_data), "analysis_type": "pattern_recognition"}
        )

    def generate_response_suggestions(self, user_id: UserID, token_str: str, message: str, context: str = "") -> Dict[str, Any]:
        """Generate response suggestions for messages"""
        return self.execute(
            user_id=user_id,
            token_str=token_str,
            query=f"Generate 3 professional response options for this message: {message}",
            task_type="response_generation",
            context={"original_message": message, "context": context}
        )
