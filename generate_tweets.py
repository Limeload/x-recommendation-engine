#!/usr/bin/env python3
"""
Quick-start script for LangChain Tweet Generator
Run this to immediately generate 50 unique tweets for any persona
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from simulation.langchain_tweet_generator import PersonaTweetGenerator


def main():
    """Main entry point"""

    print("\n" + "=" * 80)
    print("🚀 LangChain Tweet Generator - Quick Start")
    print("=" * 80)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export OPENAI_API_KEY='sk-your-api-key'")
        print("\nOr add to .env:")
        print("  OPENAI_API_KEY=sk-your-api-key")
        sys.exit(1)

    print("\n✅ OpenAI API key found\n")

    # Initialize generator
    try:
        generator = PersonaTweetGenerator(api_key=api_key)
        print("✅ LangChain initialized\n")
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        sys.exit(1)

    # Display personas
    personas = {
        "1": {
            "name": "Venture Capitalist",
            "create_func": generator.create_venture_capitalist_persona,
            "description": "Investor focused on early-stage startups and market trends"
        },
        "2": {
            "name": "Backend Engineer",
            "create_func": generator.create_engineer_persona,
            "description": "Full-stack engineer passionate about systems design"
        },
        "3": {
            "name": "Founder",
            "create_func": generator.create_founder_persona,
            "description": "Early-stage founder building in AI/tech space"
        },
    }

    print("Available personas:")
    print("-" * 80)
    for key, info in personas.items():
        print(f"\n  {key}. {info['name']}")
        print(f"     {info['description']}")

    # Get user choice
    print("\n" + "-" * 80)
    choice = input("Select persona (1-3): ").strip()

    if choice not in personas:
        print("❌ Invalid choice")
        sys.exit(1)

    persona_info = personas[choice]
    persona = persona_info["create_func"]()

    print(f"\n✅ Selected: {persona.name}")
    print(f"   Tone: {persona.tone}")
    print(f"   Tweet styles: {', '.join(persona.tweet_styles[:4])}...")

    # Get count
    print("\n" + "-" * 80)
    count_input = input("Number of tweets to generate (default: 50): ").strip()
    count = int(count_input) if count_input.isdigit() else 50
    count = max(1, min(100, count))  # Clamp to 1-100

    print(f"\n🔄 Generating {count} tweets...")
    print("-" * 80)

    # Generate tweets
    try:
        tweets = generator.generate_tweets_batch(persona, count=count, show_progress=True)
    except Exception as e:
        print(f"\n❌ Error generating tweets: {e}")
        sys.exit(1)

    # Display sample
    print("\n" + "=" * 80)
    print("Sample tweets (first 5):")
    print("=" * 80)

    for i, tweet in enumerate(tweets[:5], 1):
        print(f"\n{i}. {tweet.content}")
        print(f"   📌 Topics: {', '.join(tweet.topics)}")
        print(f"   🎯 Style: {tweet.style}")

    if len(tweets) > 5:
        print(f"\n... and {len(tweets) - 5} more tweets\n")

    # Export options
    print("-" * 80)
    print("Export options:")
    print("  1. JSON (default)")
    print("  2. CSV")
    print("  3. Skip export")

    export_choice = input("\nExport format (1-3): ").strip() or "1"

    if export_choice in ["1", "2"]:
        format_map = {"1": "json", "2": "csv"}
        format_type = format_map[export_choice]
        ext = format_type

        filename = f"tweets_{persona.name.lower().replace(' ', '_')}.{ext}"
        filepath = Path(__file__).parent / "output" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            generator.export_tweets(tweets, format=format_type, filepath=str(filepath))
            print(f"\n✅ Exported {count} tweets to: {filepath}")
        except Exception as e:
            print(f"\n❌ Export error: {e}")

    print("\n" + "=" * 80)
    print("✨ Done! Check output/ folder for generated tweets")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
