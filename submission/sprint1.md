# Sprint 1 Submission - Team ReplikaIITB


##  **Core Implementation - Two Agents**

### 🛒 **1. Shopping Agent** - Advanced Personalization ⭐ **ENHANCED**
**File**: `hushh_mcp/agents/shopping.py`
- **ML-Powered Recommendations**: Sophisticated scoring algorithm with user personalization (compatibility + savings + urgency)
- **Real-World Use Cases**: Apple products, fashion deals, electronics with actual pricing and expiration times
- **Dual API Design**: Legacy compatibility (`search_deals()`) + Enhanced API (`get_personalized_recommendations()`)
- **Dynamic User Profiling**: Simulates 3 distinct user personas (tech, fashion, books) with different preferences
- **Fallback Strategy**: Graceful degradation when personalization data unavailable
- **Consent Integration**: Requires VAULT_READ_EMAIL scope for personalization
- **Test Coverage**: 20+ comprehensive test methods + Enhanced demo script

**Key Innovation**: Multi-dimensional scoring (compatibility×0.5 + savings×0.3 + urgency×1.0-1.3 + time_sensitivity×1.0-1.2) with exploration randomness for discovery.

### 🤖 **2. AI Assistant Agent** - Advanced Conversational AI
**File**: `hushh_mcp/agents/ai_assistant.py`
- **Multi-Model Architecture**: GPT-4 → Claude-3 → Llama-3 → Rule-based fallback chain
- **Advanced Prompt Engineering**: Task-specific system prompts with context management
- **Privacy-First Design**: Respects consent boundaries, encrypted context handling
- **Specialized Tasks**: Email summarization, data analysis, response generation
- **Context Memory**: Maintains conversation history with personalization




## 🔐 **Security Implementation**

### **Consent-First Architecture**
- Every action requires explicit user consent
- Token-based validation with HMAC-SHA256
- Scope-based permissions (vault.*, agent.*)
- Automatic token expiration and cleanup

### **Data Protection**
- AES-256-GCM encryption for all user data
- Per-user encrypted storage directories
- Secure key management with environment variables
- Data sovereignty with user control

## 🚀 **Demo Instructions**

### **Quick Start**
```bash
# 1. Start development server
python start_dev.py

# 2. Open browser
http://localhost:5000

# 3. Try the agents
# - Shopping: Get personalized deals
# - AI Assistant: Chat and get insights
```

### **API Endpoints**
```bash
# Enhanced Shopping Agent (NEW!)
POST /api/agents/shopping/deals
{
  "user_id": "demo_user",
  "consent_token": "your_token_here"
}
# Returns: personalized deals with ML scoring, user profiling, and metadata

# AI Assistant
POST /api/agents/ai-assistant/chat
{
  "user_id": "demo_user", 
  "consent_token": "your_token_here",
  "query": "Help me organize my schedule"
}
```

### **🆕 Enhanced Shopping Features Demo**
```bash
# Test the enhanced shopping agent with different user profiles
python test_enhanced_shopping.py

# Shows:
# - Different personalization for tech vs fashion vs book users
# - ML scoring with confidence levels
# - Legacy API compatibility
# - Fallback strategies in action
```

---

**Team ReplikaIITB** | **Sprint 1 Complete** 
