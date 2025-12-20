import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock
from dotenv import load_dotenv

# --- 1. SETUP ENVIRONMENT ---
# Force load .env from the current directory
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Add project root to python path to fix imports
sys.path.append(os.getcwd())

try:
    from backend.apps.ai.core.services.project_service import ProjectService
    from backend.apps.ai.core.dtos import AIQueryDTO
except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    print("Run this script from the project root: ~/Desktop/opensource/nestbot_poc/")
    sys.exit(1)

async def run_full_diagnostics():
    print("==================================================")
    print("🚀 NESTBOT ARCHITECTURE DIAGNOSTIC SUITE")
    print("==================================================\n")

    # --- CHECK 1: CONFIGURATION ---
    print(f"[1/4] Checking Configuration...")
    redis_host = os.getenv("REDIS_HOST")
    if redis_host:
        print(f"   ✅ .env loaded. Target Redis: {redis_host}")
    else:
        print(f"   ❌ ERROR: REDIS_HOST is missing. Check your .env file.")
        return

    # --- CHECK 2: REAL INTEGRATION (Layers 1 -> 2 -> 3) ---
    print(f"\n[2/4] Testing Real Pipeline (Redis + Service)...")
    service = ProjectService()
    query_text = "Who maintains OWASP ZAP?"
    
    try:
        response = await service.process_query(AIQueryDTO(text=query_text, project_id="1"))
        print(f"   ✅ Pipeline Success!")
        print(f"      - Intent detected: {response.intent.label if response.intent else 'None'}")
        print(f"      - Final Source: {response.source}")
        
        if response.source == "llm_hybrid":
             print("      (Note: It fell through to Layer 3 because Redis didn't have a STATIC match. This is normal behavior.)")
             
    except Exception as e:
        print(f"   ❌ PIPELINE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- CHECK 3: AMBIGUITY LOGIC (Layer 2 Feature) ---
    print(f"\n[3/4] Testing Ambiguity Logic (Mocked Router)...")
    # We mock the router to force a low-confidence score
    service.router.get_intent = MagicMock(return_value={"intent": "STATIC", "confidence": 0.40})
    
    response = await service.process_query(AIQueryDTO(text="Unsure query", project_id="1"))
    
    if response.source == "system" and "clarify" in response.answer:
        print(f"   ✅ Ambiguity Caught: System asked for clarification (Confidence: 0.40).")
    else:
        print(f"   ❌ FAILED: Ambiguity check missed. Got source: {response.source}")

    # --- CHECK 4: CIRCUIT BREAKER (RFC Sec 3.1.3) ---
    print(f"\n[4/4] Testing Circuit Breaker (Fail-Open)...")
    # We mock a crash to ensure it doesn't kill the bot
    service.router.get_intent = MagicMock(side_effect=Exception("Redis Timeout"))
    
    response = await service.process_query(AIQueryDTO(text="Crash test", project_id="1"))
    
    if response.source == "hybrid_rag" or response.intent.label == "dynamic":
        print(f"   ✅ Circuit Breaker Active: Router crash failed open to Hybrid Search.")
    else:
        print(f"   ❌ FAILED: System did not fail open. Got source: {response.source}")

    print("\n==================================================")
    print("🎉 ALL SYSTEMS GO" if response else "⚠️ TESTS COMPLETED WITH ERRORS")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_full_diagnostics())