#!/usr/bin/env python3
"""
Manual test script for the LangGraph agent workflow.

This script tests the planner and scripter nodes with the Groq LLM API.

Usage:
    cd backend
    source venv/bin/activate
    python scripts/test_workflow.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.agents.state import create_initial_state
from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT,
    create_planner_prompt,
)
from app.agents.prompts.scripter_prompts import (
    SCRIPTER_SYSTEM_PROMPT,
    create_scripter_prompt,
)


def check_config():
    """Check that all required configuration is present."""
    settings = get_settings()
    
    print("=" * 60)
    print("Configuration Check")
    print("=" * 60)
    
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Groq API Key: {'✅ Set' if settings.groq_api_key and settings.groq_api_key != 'your_groq_api_key' else '❌ Not set'}")
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Supabase Key: {'✅ Set' if settings.supabase_key else '❌ Not set'}")
    
    if not settings.groq_api_key or settings.groq_api_key == 'your_groq_api_key':
        print("\n❌ ERROR: Please set your GROQ_API_KEY in backend/.env")
        print("   Get your key from: https://console.groq.com/keys")
        return False
    
    print("\n✅ Configuration looks good!")
    return True


async def test_groq_connection():
    """Test that we can connect to Groq API."""
    from langchain_groq import ChatGroq
    
    settings = get_settings()
    
    print("\n" + "=" * 60)
    print("Testing Groq API Connection")
    print("=" * 60)
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=settings.groq_api_key,
        )
        
        response = await llm.ainvoke([
            {"role": "user", "content": "Say 'Hello from Groq!' in exactly 5 words."}
        ])
        
        print(f"Groq Response: {response.content}")
        print("✅ Groq API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return False


async def test_planner_node():
    """Test the planner agent with a sample topic."""
    from langchain_groq import ChatGroq
    
    settings = get_settings()
    
    print("\n" + "=" * 60)
    print("Testing Planner Agent")
    print("=" * 60)
    
    test_prompt = "Explain the Pythagorean theorem for high school students"
    
    print(f"Test Topic: {test_prompt}")
    print("\nGenerating video plan...")
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=settings.groq_api_key,
        )
        
        prompt = create_planner_prompt(
            user_prompt=test_prompt,
            syllabus_context="",  # No syllabus for this test
        )
        
        response = await llm.ainvoke([
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        
        print("\n--- Raw Response ---")
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        
        # Try to parse JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        plan = json.loads(content.strip())
        
        print("\n--- Parsed Plan ---")
        print(f"Title: {plan.get('title', 'N/A')}")
        print(f"Learning Objectives: {plan.get('learning_objectives', [])}")
        print(f"Number of Scenes: {len(plan.get('scenes', []))}")
        
        for scene in plan.get('scenes', []):
            print(f"  - Scene {scene.get('scene_number')}: {scene.get('title')} ({scene.get('duration_seconds')}s)")
        
        print("\n✅ Planner agent working correctly!")
        return plan
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        print(f"❌ Planner Error: {e}")
        return None


async def test_scripter_node(plan: dict):
    """Test the scripter agent with the first scene from the plan."""
    from langchain_groq import ChatGroq
    
    if not plan or not plan.get('scenes'):
        print("\n⚠️  Skipping scripter test (no plan available)")
        return
    
    settings = get_settings()
    
    print("\n" + "=" * 60)
    print("Testing Scripter Agent")
    print("=" * 60)
    
    scene_plan = plan['scenes'][0]  # Test with first scene
    video_title = plan.get('title', 'Test Video')
    
    print(f"Testing with Scene 1: {scene_plan.get('title', 'Unknown')}")
    print("\nGenerating script...")
    
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=settings.groq_api_key,
        )
        
        prompt = create_scripter_prompt(
            scene_plan=scene_plan,
            scene_index=0,
            video_title=video_title,
        )
        
        response = await llm.ainvoke([
            {"role": "system", "content": SCRIPTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        
        print("\n--- Raw Response ---")
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        
        # Try to parse JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        script = json.loads(content.strip())
        
        print("\n--- Parsed Script ---")
        print(f"Scene Order: {script.get('scene_order')}")
        print(f"Duration: {script.get('duration_estimate')}s")
        print(f"\nNarration:\n{script.get('narration', 'N/A')[:200]}...")
        print(f"\nVisual Description:\n{script.get('visual_description', 'N/A')[:200]}...")
        
        print("\n✅ Scripter agent working correctly!")
        return script
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        print(f"❌ Scripter Error: {e}")
        return None


async def main():
    """Run all tests."""
    print("\n🚀 LangGraph Workflow Manual Test")
    print("=" * 60)
    
    # Step 1: Check configuration
    if not check_config():
        return
    
    # Step 2: Test Groq connection
    if not await test_groq_connection():
        return
    
    # Step 3: Test Planner
    plan = await test_planner_node()
    
    # Step 4: Test Scripter (if planner worked)
    if plan:
        await test_scripter_node(plan)
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start your local Supabase: supabase start")
    print("2. Start the FastAPI server: uvicorn app.main:app --reload")
    print("3. Create a video via the API to test the full flow")


if __name__ == "__main__":
    asyncio.run(main())
