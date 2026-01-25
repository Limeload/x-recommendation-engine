"""
Testing examples for LangChain Tweet Generator
Run these to validate the system works with your setup
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from simulation.langchain_tweet_generator import PersonaTweetGenerator, PersonaTemplate


def test_basic_generation():
    """Test basic tweet generation"""
    print("\n" + "="*70)
    print("TEST 1: Basic Tweet Generation")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()
        print("✅ Generator initialized")

        persona = generator.create_venture_capitalist_persona()
        print(f"✅ Persona created: {persona.name}")

        tweet = generator.generate_tweet(persona)
        print(f"✅ Tweet generated: {tweet.content[:50]}...")
        print(f"   Topics: {tweet.topics}")
        print(f"   Style: {tweet.style}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_generation():
    """Test batch generation"""
    print("\n" + "="*70)
    print("TEST 2: Batch Generation (5 tweets)")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()
        persona = generator.create_engineer_persona()

        tweets = generator.generate_tweets_batch(persona, count=5, show_progress=True)
        print(f"\n✅ Generated {len(tweets)} tweets")

        for i, tweet in enumerate(tweets, 1):
            print(f"\n{i}. {tweet.content[:60]}...")
            print(f"   Style: {tweet.style}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_all_personas():
    """Test all three personas"""
    print("\n" + "="*70)
    print("TEST 3: All Personas")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()

        personas = [
            ("Venture Capitalist", generator.create_venture_capitalist_persona()),
            ("Engineer", generator.create_engineer_persona()),
            ("Founder", generator.create_founder_persona()),
        ]

        for name, persona in personas:
            print(f"\n📌 {name}")
            print(f"   Tone: {persona.tone}")
            print(f"   Styles: {len(persona.tweet_styles)}")
            print(f"   Interests: {len(persona.interests)}")
            print(f"   Expertise: {len(persona.expertise)}")

            # Generate one tweet
            tweet = generator.generate_tweet(persona)
            print(f"   Sample: {tweet.content[:50]}...")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_export():
    """Test export functionality"""
    print("\n" + "="*70)
    print("TEST 4: Export Functionality")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()
        persona = generator.create_founder_persona()

        tweets = generator.generate_tweets_batch(persona, count=3, show_progress=False)

        # Test JSON export
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)

        json_file = output_dir / "test_tweets.json"
        generator.export_tweets(tweets, format="json", filepath=str(json_file))

        if json_file.exists():
            print(f"✅ JSON export successful: {json_file}")
            print(f"   File size: {json_file.stat().st_size} bytes")

        # Test CSV export
        csv_file = output_dir / "test_tweets.csv"
        generator.export_tweets(tweets, format="csv", filepath=str(csv_file))

        if csv_file.exists():
            print(f"✅ CSV export successful: {csv_file}")
            print(f"   File size: {csv_file.stat().st_size} bytes")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_custom_persona():
    """Test custom persona creation"""
    print("\n" + "="*70)
    print("TEST 5: Custom Persona")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()

        custom = PersonaTemplate(
            name="Data Analyst",
            description="Analytics-focused professional",
            interests=["Data", "Analytics", "SQL", "Python", "Visualization"],
            expertise=["Data modeling", "SQL optimization", "Dashboard design"],
            tone="analytical",
            tweet_styles=["data_insight", "methodology_discussion"],
        )

        print(f"✅ Custom persona created: {custom.name}")
        print(f"   Interests: {custom.interests}")

        # Note: Generating with custom persona requires sample templates
        # which we don't have in this test, so we skip generation
        print("   (Skipping generation - requires extended template)")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_configuration():
    """Test LLM configuration"""
    print("\n" + "="*70)
    print("TEST 6: Configuration")
    print("="*70)

    try:
        generator = PersonaTweetGenerator()

        # Check default settings
        print(f"✅ Default temperature: {generator.llm.temperature}")
        print(f"   Default max_tokens: {generator.llm.max_tokens}")
        print(f"   Model: gpt-3.5-turbo")

        # These settings are read-only at runtime, but we can verify they exist
        assert hasattr(generator.llm, 'temperature')
        assert hasattr(generator.llm, 'max_tokens')
        print("✅ Configuration attributes verified")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 LangChain Tweet Generator - Test Suite")
    print("="*70)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("   Tests requiring LLM will fail")
        print("   Set with: export OPENAI_API_KEY='sk-...'")
    else:
        print(f"\n✅ API key found (first 10 chars: {api_key[:10]}...)")

    tests = [
        ("Basic Generation", test_basic_generation),
        ("Batch Generation", test_batch_generation),
        ("All Personas", test_all_personas),
        ("Export", test_export),
        ("Custom Persona", test_custom_persona),
        ("Configuration", test_configuration),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
