#!/usr/bin/env python3
"""
Quick start script for HushhMCP development.
Simple development server setup for hackathon demo.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🤫 HushhMCP - Quick Start")
    print("=" * 30)
    
    # Create vault directory
    vault_dir = Path("vault_data")
    vault_dir.mkdir(exist_ok=True)
    print(f"📁 Vault directory: {vault_dir.absolute()}")
    
    # Set environment variables
    os.environ["SECRET_KEY"] = "dev_secret_key_change_in_production"
    os.environ["VAULT_ENCRYPTION_KEY"] = "dev_encryption_key_32_chars_long_change_in_production_please"
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "true"
    
    print("🔧 Environment configured for development")
    
    # Check if requirements are installed
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the Flask app
    print("🚀 Starting development server...")
    print("🌐 Web app will be available at: http://localhost:5000")
    print("📊 Try these endpoints:")
    print("   GET  / - Main web interface")
    print("   POST /api/consent/request - Request consent")
    print("   POST /api/agents/shopping/deals - Shopping agent")
    print("   GET  /api/health - Health check")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError:
        print("❌ Could not import app.py")
        print("Make sure you're in the project root directory")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Shutting down development server")
        return 0

if __name__ == "__main__":
    sys.exit(main())
