#!/usr/bin/env python3
"""
Quick Start: Exploration-Exploitation Layer Example
Demonstrates how to use Thompson Sampling, Epsilon-Greedy, and UCB strategies
to inject exploratory content into feeds.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.inmemory_db import InMemoryDB
from models.schemas import User, Tweet, EngagementMetrics
from models.ranking_engine import RankingEngine
from models.exploration_ranker import ExplorationStrategy


def create_sample_feed():
    """Create sample tweets for demonstration"""
    tweets = [
        Tweet(
            tweet_id=f"tweet-{i}",
            author_id=f"author-{i % 5}",
            content=f"Sample tweet {i}: {topics[i % len(topics)]} content",
            topics=[topics[i % len(topics)]],
            engagement=EngagementMetrics(
                likes=100 + i * 20,
                retweets=20 + i * 5,
                replies=5 + i * 2,
            ),
            quality_score=0.7 + (i % 3) * 0.1,
            created_at=datetime.utcnow() - timedelta(hours=i),
        )
        for i in range(30)
    ]
    return tweets


topics = [
    "AI", "Startups", "Technology", "Business", "Science",
    "AI", "Startups", "Technology", "Business", "Science"
]


def example_1_epsilon_greedy():
    """Example 1: Simple Epsilon-Greedy exploration"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Epsilon-Greedy Strategy (Simple & Effective)")
    print("="*70)

    # Create user
    user = User(
        id="user-1",
        username="tech_investor",
        name="Tech Investor",
        interests=["AI", "Startups", "Technology"],
        expertise_areas=["Venture Capital"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        }
    )

    # Create ranking engine with Epsilon-Greedy (default)
    engine = RankingEngine(
        user=user,
        enable_exploration=True,
        exploration_rate=0.10,  # 10% of feed
        exploration_strategy=ExplorationStrategy.EPSILON_GREEDY
    )

    print("\n✅ Created RankingEngine with Epsilon-Greedy strategy")
    print(f"   Exploration Rate: 10%")
    print(f"   Strategy: Random selection from exploration pool")

    # Get sample feed
    feed = create_sample_feed()

    # Rank with exploration
    ranked, explanations = engine.rank_tweets(
        candidates=feed,
        num_to_return=10
    )

    print(f"\n📊 Generated feed with 10 tweets:")

    # Show breakdown
    exploitation_count = sum(1 for exp in explanations if exp["selected_for"] == "exploitation")
    exploration_count = sum(1 for exp in explanations if exp["selected_for"] == "exploration")

    print(f"   Exploitation (highest-ranked): {exploitation_count}")
    print(f"   Exploration (exploratory): {exploration_count}")

    # Show first few tweets
    print(f"\n📝 First 3 tweets in feed:")
    for i, (tweet, exp) in enumerate(zip(ranked[:3], explanations[:3]), 1):
        print(f"   {i}. {tweet.tweet.content[:50]}...")
        print(f"      Type: {exp['selected_for']} | Reason: {exp['reason']}")

    return engine


def example_2_thompson_sampling():
    """Example 2: Thompson Sampling with learning"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Thompson Sampling (Learning & Adaptation)")
    print("="*70)

    # Create user
    user = User(
        id="user-2",
        username="venture_capitalist",
        name="Venture Capitalist",
        interests=["Startups", "Fundraising"],
        expertise_areas=["Due Diligence", "Valuation"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        }
    )

    # Create ranking engine with Thompson Sampling
    engine = RankingEngine(
        user=user,
        enable_exploration=True,
        exploration_rate=0.10,
        exploration_strategy=ExplorationStrategy.THOMPSON_SAMPLING
    )

    print("\n✅ Created RankingEngine with Thompson Sampling strategy")
    print(f"   Exploration Rate: 10%")
    print(f"   Strategy: Bayesian sampling with Beta distribution")

    # Simulate 3 days of feedback
    feed = create_sample_feed()

    for day in range(1, 4):
        print(f"\n📅 Day {day}:")

        ranked, explanations = engine.rank_tweets(
            candidates=feed,
            num_to_return=10
        )

        # Simulate user engagement
        print(f"   User sees 10 tweets, engages with first 7...")
        for i in range(7):
            engine.record_engagement_for_exploration(
                tweet_id=ranked[i].tweet.tweet_id,
                author_id=ranked[i].tweet.author_id,
                engagement_type="like" if i < 5 else "view"
            )

        # Show learning progress
        stats = engine.get_exploration_stats()
        print(f"   Authors tracked: {stats['total_authors_tracked']}")
        print(f"   Average engagement rate: {stats['average_engagement_rate']:.1%}")

    # Final stats
    final_stats = engine.get_exploration_stats()
    print(f"\n📊 Final Learning Summary:")
    print(f"   Authors tracked: {final_stats['total_authors_tracked']}")
    print(f"   Average engagement rate: {final_stats['average_engagement_rate']:.1%}")
    print(f"   Std dev: {final_stats['engagement_rate_std']:.1%}")

    return engine


def example_3_ucb():
    """Example 3: Upper Confidence Bound (UCB) strategy"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Upper Confidence Bound (UCB) - Optimistic Exploration")
    print("="*70)

    # Create user
    user = User(
        id="user-3",
        username="founder",
        name="Startup Founder",
        interests=["Product", "Growth", "AI"],
        expertise_areas=["Product Management"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        }
    )

    # Create ranking engine with UCB
    engine = RankingEngine(
        user=user,
        enable_exploration=True,
        exploration_rate=0.15,  # Slightly more exploration for UCB
        exploration_strategy=ExplorationStrategy.UCB
    )

    print("\n✅ Created RankingEngine with UCB strategy")
    print(f"   Exploration Rate: 15%")
    print(f"   Strategy: Empirical rate + optimistic uncertainty bonus")

    feed = create_sample_feed()

    # Pre-populate some author stats
    engine.exploration_ranker.stats["author_author-0"] = type(
        'ExplorationStats',
        (),
        {'successes': 50, 'failures': 10, 'total_trials': 60}
    )()

    ranked, explanations = engine.rank_tweets(
        candidates=feed,
        num_to_return=10
    )

    print(f"\n📊 Generated feed with 10 tweets:")

    # Show breakdown
    exploration_items = [exp for exp in explanations if exp["selected_for"] == "exploration"]

    print(f"   Exploration items: {len(exploration_items)}")
    print(f"\n   UCB selects items with:")
    print(f"   - High engagement potential (sampled from posterior)")
    print(f"   - High uncertainty (fewer exposures)")

    # Show example explanation
    if exploration_items:
        print(f"\n   Example exploration reason:")
        print(f"   '{exploration_items[0]['reason']}'")

    return engine


def example_4_ab_testing():
    """Example 4: A/B Testing different strategies"""
    print("\n" + "="*70)
    print("EXAMPLE 4: A/B Testing Strategies")
    print("="*70)

    # Create two users
    user_a = User(
        id="user-a",
        username="user_a",
        name="User A (Epsilon-Greedy)",
        interests=["AI", "Tech"],
        expertise_areas=["Engineering"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        }
    )

    user_b = User(
        id="user-b",
        username="user_b",
        name="User B (Thompson Sampling)",
        interests=["AI", "Tech"],
        expertise_areas=["Engineering"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        }
    )

    # Create engines with different strategies
    engine_a = RankingEngine(
        user=user_a,
        enable_exploration=True,
        exploration_rate=0.10,
        exploration_strategy=ExplorationStrategy.EPSILON_GREEDY
    )

    engine_b = RankingEngine(
        user=user_b,
        enable_exploration=True,
        exploration_rate=0.10,
        exploration_strategy=ExplorationStrategy.THOMPSON_SAMPLING
    )

    print("\n✅ Created two ranking engines with different strategies:")
    print(f"   Group A: Epsilon-Greedy")
    print(f"   Group B: Thompson Sampling")

    feed = create_sample_feed()

    # Simulate 5 rounds
    for round_num in range(1, 6):
        ranked_a, _ = engine_a.rank_tweets(candidates=feed, num_to_return=10)
        ranked_b, _ = engine_b.rank_tweets(candidates=feed, num_to_return=10)

        # Simulate engagement
        for i in range(8):
            engine_a.record_engagement_for_exploration(
                ranked_a[i].tweet.tweet_id,
                ranked_a[i].tweet.author_id,
                "like"
            )
            engine_b.record_engagement_for_exploration(
                ranked_b[i].tweet.tweet_id,
                ranked_b[i].tweet.author_id,
                "like"
            )

    # Compare results
    stats_a = engine_a.get_exploration_stats()
    stats_b = engine_b.get_exploration_stats()

    print(f"\n📊 After 5 rounds of A/B testing:")
    print(f"   Group A (Epsilon-Greedy):")
    print(f"     Average engagement rate: {stats_a['average_engagement_rate']:.1%}")
    print(f"     Authors tracked: {stats_a['total_authors_tracked']}")

    print(f"\n   Group B (Thompson Sampling):")
    print(f"     Average engagement rate: {stats_b['average_engagement_rate']:.1%}")
    print(f"     Authors tracked: {stats_b['total_authors_tracked']}")

    # Winner
    winner = "A (Epsilon-Greedy)" if stats_a['average_engagement_rate'] > stats_b['average_engagement_rate'] else "B (Thompson Sampling)"
    print(f"\n   🏆 Winner: Group {winner}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🚀 EXPLORATION-EXPLOITATION LAYER - QUICK START EXAMPLES")
    print("="*70)

    # Example 1: Epsilon-Greedy
    engine1 = example_1_epsilon_greedy()

    # Example 2: Thompson Sampling
    engine2 = example_2_thompson_sampling()

    # Example 3: UCB
    engine3 = example_3_ucb()

    # Example 4: A/B Testing
    example_4_ab_testing()

    # Summary
    print("\n" + "="*70)
    print("✨ SUMMARY")
    print("="*70)
    print("\n📚 Key Takeaways:")
    print("   • Epsilon-Greedy: Simple, random exploration (baseline)")
    print("   • Thompson Sampling: Learns from feedback, adapts over time")
    print("   • UCB: Theoretically optimal, self-adjusting exploration")
    print("\n🎯 Default: Epsilon-Greedy with 10% exploration rate")
    print("   Can be changed with:")
    print("     - exploration_strategy parameter in RankingEngine()")
    print("     - set_exploration_strategy() method at runtime")
    print("\n📊 Track performance with:")
    print("     - record_engagement_for_exploration()")
    print("     - get_exploration_stats()")
    print("\n📖 Read EXPLORATION_LAYER_GUIDE.md for detailed documentation")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
