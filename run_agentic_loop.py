#!/usr/bin/env python3
"""
Quick Start Example: Run the Agentic Loop with sample personas
Execute this to see agents autonomously interact with the feed
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.inmemory_db import InMemoryDB
from models.schemas import User, Tweet, EngagementMetrics
from simulation.agentic_loop import AgentManager
from simulation.langchain_tweet_generator import PersonaTweetGenerator
from datetime import datetime, timedelta
import random


async def main():
    """Run agentic loop example"""

    print("\n" + "=" * 70)
    print("🤖 AGENTIC LOOP - Quick Start Example")
    print("=" * 70)

    # Initialize database
    db = InMemoryDB()
    print("\n✅ Database initialized")

    # Create persona agents
    print("\n📋 Creating persona agents...")

    manager = AgentManager(db, api_key=None)  # No LLM for quick demo

    # Create personas
    personas = [
        {
            "id": "vc-1",
            "name": "Venture Capitalist",
            "type": "venture_capitalist",
            "interests": ["Startups", "AI", "Fintech", "Funding"],
            "expertise": ["Due diligence", "Valuation"],
            "threshold": 0.5,
            "reply_prob": 0.2,
        },
        {
            "id": "eng-1",
            "name": "Backend Engineer",
            "type": "engineer",
            "interests": ["Systems Design", "DevOps", "AI", "Performance"],
            "expertise": ["Distributed systems", "API design"],
            "threshold": 0.6,
            "reply_prob": 0.1,
        },
        {
            "id": "founder-1",
            "name": "Founder",
            "type": "founder",
            "interests": ["Product", "Growth", "AI", "Startups"],
            "expertise": ["Product management", "Growth hacking"],
            "threshold": 0.4,
            "reply_prob": 0.3,
        },
    ]

    for persona in personas:
        user = User(
            id=persona["id"],
            name=persona["name"],
            persona_type=persona["type"],
            interests=persona["interests"],
            expertise=persona["expertise"],
        )
        manager.create_agent(
            user,
            engagement_threshold=persona["threshold"],
            reply_probability=persona["reply_prob"],
        )
        print(f"  ✅ {persona['name']}")

    # Generate sample tweets using LangChain (if available)
    print("\n📝 Generating sample tweets...")

    # Create sample tweets manually for quick demo
    sample_tweets = [
        Tweet(
            id="tweet-1",
            author_id="user-1",
            content="Just launched our AI-powered fintech startup! Raising seed round soon.",
            topics=["AI", "Fintech", "Startups"],
            engagement=EngagementMetrics(likes=150, retweets=45),
            quality_score=0.85,
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
        Tweet(
            id="tweet-2",
            author_id="user-2",
            content="New blog post on distributed systems and eventual consistency patterns",
            topics=["Systems Design", "DevOps", "Architecture"],
            engagement=EngagementMetrics(likes=200, retweets=80),
            quality_score=0.9,
            created_at=datetime.utcnow() - timedelta(hours=1),
        ),
        Tweet(
            id="tweet-3",
            author_id="user-3",
            content="Product-market fit is overrated. Customer obsession is underrated.",
            topics=["Product", "Growth", "Strategy"],
            engagement=EngagementMetrics(likes=500, retweets=120),
            quality_score=0.88,
            created_at=datetime.utcnow() - timedelta(minutes=30),
        ),
        Tweet(
            id="tweet-4",
            author_id="user-4",
            content="Why the best founders think long-term while building short-term",
            topics=["Startups", "Founder", "Growth"],
            engagement=EngagementMetrics(likes=300, retweets=90),
            quality_score=0.87,
            created_at=datetime.utcnow() - timedelta(hours=3),
        ),
        Tweet(
            id="tweet-5",
            author_id="user-5",
            content="AI models are getting cheaper but data quality is priceless",
            topics=["AI", "Data", "ML"],
            engagement=EngagementMetrics(likes=400, retweets=100),
            quality_score=0.86,
            created_at=datetime.utcnow() - timedelta(hours=4),
        ),
        Tweet(
            id="tweet-6",
            author_id="user-6",
            content="Just baked a sourdough bread, turned out great!",
            topics=["Baking", "Food"],
            engagement=EngagementMetrics(likes=50, retweets=10),
            quality_score=0.5,
            created_at=datetime.utcnow() - timedelta(hours=5),
        ),
    ]

    for tweet in sample_tweets:
        db.add_tweet(tweet)

    print(f"  ✅ {len(sample_tweets)} sample tweets created")

    # Run agentic loop
    print("\n" + "=" * 70)
    print("🔄 RUNNING AGENTIC LOOP")
    print("=" * 70)

    await manager.run_agentic_loop(num_cycles=2)

    # Display results
    print("\n" + "=" * 70)
    print("📊 AGENTIC LOOP RESULTS")
    print("=" * 70)

    summary = {
        "total_agents": len(manager.agents),
        "total_engagements": 0,
        "engagement_types": {"like": 0, "reply": 0, "retweet": 0, "bookmark": 0},
    }

    for agent in manager.get_all_agents():
        stats = manager.get_agent_stats(agent.user.id)

        print(f"\n👤 {stats['user_name']}")
        print(f"   Total Engagements: {stats['total_engagements']}")
        print(f"   Breakdown: {stats['engagement_counts']}")
        print(f"   Avg Confidence: {stats['average_confidence']:.2f}")
        print(f"   Interests: {', '.join(stats['interests'][:3])}")

        summary["total_engagements"] += stats["total_engagements"]
        for key, count in stats["engagement_counts"].items():
            summary["engagement_types"][key] += count

        # Show recent decisions
        history = agent.engagement_history[-3:]
        if history:
            print(f"   Recent Decisions:")
            for decision in history:
                print(f"     - {decision.decision.value.upper()} tweet {decision.tweet_id[:10]}... ({decision.confidence:.2f})")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Agents: {summary['total_agents']}")
    print(f"Total Engagements: {summary['total_engagements']}")
    print(f"Engagement Breakdown:")
    for engagement_type, count in summary["engagement_types"].items():
        print(f"  - {engagement_type.upper()}: {count}")

    # Show engagement impact on tweets
    print("\n" + "=" * 70)
    print("📈 TWEET ENGAGEMENT METRICS (After Agentic Loop)")
    print("=" * 70)

    for tweet in sample_tweets[:5]:
        updated_tweet = db.tweets[tweet.id]
        total_engagement = (
            updated_tweet.engagement.likes
            + updated_tweet.engagement.retweets
            + updated_tweet.engagement.replies
        )
        print(
            f"\n'{updated_tweet.content[:50]}...'"
        )
        print(f"  👍 Likes: {updated_tweet.engagement.likes}")
        print(f"  🔄 Retweets: {updated_tweet.engagement.retweets}")
        print(f"  💬 Replies: {updated_tweet.engagement.replies}")
        print(f"  📌 Total: {total_engagement}")

    print("\n" + "=" * 70)
    print("✨ Agentic Loop Complete!")
    print("=" * 70 + "\n")

    print("📚 Next Steps:")
    print("  1. Read AGENTIC_LOOP_GUIDE.md for detailed documentation")
    print("  2. Run with API enabled for LLM-powered replies:")
    print("     export OPENAI_API_KEY='sk-your-key'")
    print("  3. Integrate with FastAPI endpoints:")
    print("     See backend/routes/agentic_loop_routes.py")
    print("  4. Customize agent behavior:")
    print("     Adjust engagement_threshold and reply_probability")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
