#!/usr/bin/env python3
"""
Simple run script for the AI Chatbot with RAG application.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in .env file")
    print("\nPlease follow these steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your OpenAI API key to the .env file")
    print("3. Run this script again")
    sys.exit(1)

print("Starting AI Chatbot with RAG...")
print("="*50)
print(f"Host: {os.getenv('HOST', '0.0.0.0')}")
print(f"Port: {os.getenv('PORT', '8000')}")
print("="*50)
print("\nServer will be available at: http://localhost:8000")
print("Press CTRL+C to stop the server\n")

# Import and run
import uvicorn
from backend.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)
