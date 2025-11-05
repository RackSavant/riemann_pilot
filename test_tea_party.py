#!/usr/bin/env python3
"""
Tea Party MVP - Quick Test Script

Tests the multi-dimensional steering system without video generation.
"""
import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from tea_party_conversation import TeaPartyConversationEngine


async def test_basic_conversation():
    """Test basic conversation generation"""
    print("🫖 Testing Tea Party Conversation Engine")
    print("=" * 60)
    
    try:
        # Initialize engine
        print("\n📋 Initializing conversation engine...")
        engine = TeaPartyConversationEngine()
        print("✅ Engine initialized")
        
        # Show all characters
        print("\n👥 Characters:")
        states = engine.get_all_character_states()
        for state in states:
            print(f"  - {state['character_name']} ({state['character_id']})")
        
        # Set topic
        topic = "the perfect tea party experience"
        print(f"\n💬 Topic: {topic}")
        engine.set_topic(topic)
        
        # Test different dial configurations
        print("\n🎛️  Testing Dial Configurations:")
        print("-" * 60)
        
        # Test 1: High irony
        print("\n🧪 Test 1: Alex with HIGH IRONY (0.9)")
        engine.update_character_dial("purple_person", "irony", 0.9)
        turn1 = await engine.generate_response("purple_person", generate_video=False)
        print(f"   Alex: {turn1.text}")
        
        # Test 2: Low irony
        print("\n🧪 Test 2: Alex with LOW IRONY (0.1)")
        engine.update_character_dial("purple_person", "irony", 0.1)
        turn2 = await engine.generate_response("purple_person", generate_video=False)
        print(f"   Alex: {turn2.text}")
        
        # Test 3: High empathy
        print("\n🧪 Test 3: Morgan with HIGH THEORY OF MIND (0.95)")
        engine.update_character_dial("blue_hair", "theory_of_mind", 0.95)
        turn3 = await engine.generate_response("blue_hair", generate_video=False)
        print(f"   Morgan: {turn3.text}")
        
        # Test 4: Self-focused
        print("\n🧪 Test 4: Jordan SELF-FOCUSED (0.1)")
        engine.update_character_dial("phone_person", "self_other", 0.1)
        turn4 = await engine.generate_response("phone_person", generate_video=False)
        print(f"   Jordan: {turn4.text}")
        
        # Test 5: Other-focused
        print("\n🧪 Test 5: Riley OTHER-FOCUSED (0.9)")
        engine.update_character_dial("blonde_center", "self_other", 0.9)
        turn5 = await engine.generate_response("blonde_center", generate_video=False)
        print(f"   Riley: {turn5.text}")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\n📊 Conversation History:")
        history = engine.get_conversation_history()
        print(f"   Total turns: {len(history)}")
        
        print("\n🎯 System is working! Ready to:")
        print("   1. Start the API server: cd app && python tea_party_api.py")
        print("   2. Generate videos: Set generate_video=True")
        print("   3. Build the frontend UI")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_steering_prompts():
    """Test steering prompt generation"""
    print("\n\n🎛️  Testing Steering Prompt Generation")
    print("=" * 60)
    
    from tea_party_characters import TeaPartyCharacterManager
    
    manager = TeaPartyCharacterManager()
    
    # Get Alex and adjust dials
    alex = manager.get_character("purple_person")
    alex.update_dial("theory_of_mind", 0.2)  # Low empathy
    alex.update_dial("harmfulness", 0.8)     # High harmfulness
    alex.update_dial("irony", 0.9)           # High irony
    alex.update_dial("self_other", 0.1)      # Self-focused
    
    print("\n📝 Steering Prompt for Alex with extreme dials:")
    print("-" * 60)
    prompt = alex.get_steering_prompt()
    print(prompt)
    print("-" * 60)
    
    print("\n✅ Steering prompt test complete!")


def main():
    """Run all tests"""
    print("\n" + "🫖" * 30)
    print("   TEA PARTY MVP - SYSTEM TEST")
    print("🫖" * 30)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set in environment")
        print("   Tests will fail without API key")
        print("\n   Set it with:")
        print("   export OPENAI_API_KEY=sk-...")
        return
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set")
        print("   Video generation will not work")
        print("   (Text generation will still work)")
    
    # Run tests
    asyncio.run(test_basic_conversation())
    asyncio.run(test_steering_prompts())


if __name__ == "__main__":
    main()
