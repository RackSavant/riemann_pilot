#!/usr/bin/env python3
"""
Test semantic dial validation

Demonstrates how semantic similarity proves that steering actually works.
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from semantic_dial_validator import SemanticDialValidator, TEA_PARTY_DESCRIPTORS
from tea_party_conversation import TeaPartyConversationEngine

async def test_validation():
    """Test semantic validation on steering"""
    print("🔬 Testing Semantic Dial Validation")
    print("=" * 70)
    
    # Initialize
    validator = SemanticDialValidator()
    engine = TeaPartyConversationEngine()
    
    # Test case 1: High Irony
    print("\n📊 Test 1: High Irony (90%)")
    print("-" * 70)
    
    engine.update_character_dial("purple_person", "irony", 0.9)
    turn = await engine.generate_response("purple_person", generate_video=False)
    
    print(f"Response: {turn.text}")
    print()
    
    scores = validator.validate_steering_effectiveness(
        turn.dial_values,
        turn.text,
        TEA_PARTY_DESCRIPTORS
    )
    
    print("Validation Scores:")
    for dim, score_data in scores.items():
        if isinstance(score_data, dict):
            print(f"\n  {dim}:")
            print(f"    Dial Setting: {score_data['dial_value']:.0%}")
            print(f"    Alignment: {score_data['alignment']:.1%}")
            print(f"    Low Similarity: {score_data['low_similarity']:.3f}")
            print(f"    High Similarity: {score_data['high_similarity']:.3f}")
    
    # Test case 2: Low Irony
    print("\n\n📊 Test 2: Low Irony (10%)")
    print("-" * 70)
    
    engine.update_character_dial("purple_person", "irony", 0.1)
    turn = await engine.generate_response("purple_person", generate_video=False)
    
    print(f"Response: {turn.text}")
    print()
    
    scores = validator.validate_steering_effectiveness(
        turn.dial_values,
        turn.text,
        TEA_PARTY_DESCRIPTORS
    )
    
    print("Validation Scores:")
    for dim, score_data in scores.items():
        if isinstance(score_data, dict) and dim == 'irony':
            print(f"\n  {dim}:")
            print(f"    Dial Setting: {score_data['dial_value']:.0%}")
            print(f"    Alignment: {score_data['alignment']:.1%}")
            print(f"    Low Similarity: {score_data['low_similarity']:.3f}")
            print(f"    High Similarity: {score_data['high_similarity']:.3f}")
    
    # Test case 3: Compare 3 models
    print("\n\n📊 Test 3: Compare 3 LLMs with High Harmfulness")
    print("-" * 70)
    
    engine.update_character_dial("purple_person", "harmfulness", 0.9)
    
    models = ["gpt-4", "claude", "gemini"]
    responses = {}
    
    for model in models:
        print(f"\n🤖 Generating with {model}...")
        try:
            turn = await engine.generate_response(
                "purple_person",
                generate_video=False,
                model=model
            )
            responses[model] = turn.text
            print(f"  {model}: {turn.text[:80]}...")
        except Exception as e:
            print(f"  ❌ Error with {model}: {e}")
            responses[model] = f"Error: {str(e)}"
    
    # Compare steering effectiveness across models
    print("\n\n🔍 Comparing Steering Effectiveness:")
    print("-" * 70)
    
    comparison = validator.compare_models_steering(
        responses,
        {"harmfulness": 0.9},
        {"harmfulness": TEA_PARTY_DESCRIPTORS["harmfulness"]}
    )
    
    for model, scores in comparison.items():
        if 'harmfulness' in scores and isinstance(scores['harmfulness'], dict):
            harm_score = scores['harmfulness']
            print(f"\n{model}:")
            print(f"  Alignment: {harm_score['alignment']:.1%}")
            print(f"  High (Harmful) Similarity: {harm_score['high_similarity']:.3f}")
            print(f"  Response: {responses[model][:100]}...")
    
    print("\n\n" + "=" * 70)
    print("✅ Semantic validation complete!")
    print("\nKey Insights:")
    print("  • Alignment score shows how well response matches dial setting")
    print("  • High alignment = steering is working")
    print("  • Compare across models to see which follows instructions best")
    print("  • Similarity scores quantify the steering effect")

if __name__ == "__main__":
    asyncio.run(test_validation())
