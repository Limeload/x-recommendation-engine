"""
Tests for the agentic loop system
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.database.inmemory_db import InMemoryDB
from backend.models.schemas import User, Tweet, EngagementMetrics
from backend.simulation.agentic_loop import (
    PersonaAgent,
    AgentManager,
    InterestVector,
    EngagementType,
)


@pytest.fixture
def db():
    """Create in-memory database"""
    return InMemoryDB()


@pytest.fixture
def sample_user():
    """Create sample user"""
    return User(
        id="vc-1",
        name="Venture Capitalist",
        persona_type="venture_capitalist",
        interests=["AI", "Startups", "Fintech"],
        expertise=["Due diligence", "Valuation"],
    )


@pytest.fixture
def sample_tweets(db):
    """Create sample tweets"""
    tweets = []

    # Relevant tweet
    tweet1 = Tweet(
        id="tweet-1",
        author_id="user-1",
        content="Excited about AI disruption in fintech!",
        topics=["AI", "Fintech"],
        engagement=EngagementMetrics(likes=100, retweets=50),
        quality_score=0.85,
        created_at=datetime.utcnow() - timedelta(hours=2),
    )
    db.add_tweet(tweet1)
    tweets.append(tweet1)

    # Irrelevant tweet
    tweet2 = Tweet(
        id="tweet-2",
        author_id="user-2",
        content="Just baked the best chocolate cake!",
        topics=["Food", "Baking"],
        engagement=EngagementMetrics(likes=50, retweets=20),
        quality_score=0.6,
        created_at=datetime.utcnow() - timedelta(hours=4),
    )
    db.add_tweet(tweet2)
    tweets.append(tweet2)

    # Moderately relevant tweet
    tweet3 = Tweet(
        id="tweet-3",
        author_id="user-3",
        content="New startup using machine learning for payments",
        topics=["Startups", "ML"],
        engagement=EngagementMetrics(likes=200, retweets=80),
        quality_score=0.8,
        created_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.add_tweet(tweet3)
    tweets.append(tweet3)

    return tweets


def test_interest_vector_relevance():
    """Test interest vector relevance computation"""
    vector = InterestVector(interests={"AI": 1.0, "Startups": 0.8, "Fintech": 0.9})

    # Test exact match
    relevance = vector.compute_relevance(["AI", "Innovation"])
    assert relevance > 0.3

    # Test no match
    relevance = vector.compute_relevance(["Food", "Cooking"])
    assert relevance == 0.0

    # Test multiple matches
    relevance = vector.compute_relevance(["AI", "Startups"])
    assert relevance > 0.5


def test_persona_agent_evaluation(db, sample_user, sample_tweets):
    """Test agent tweet evaluation"""
    agent = PersonaAgent(sample_user, db)

    # Evaluate relevant tweet
    should_engage, confidence, reason = agent.evaluate_tweet(sample_tweets[0])
    assert should_engage is True
    assert confidence > 0.5
    assert reason != ""

    # Evaluate irrelevant tweet
    should_engage, confidence, reason = agent.evaluate_tweet(sample_tweets[1])
    assert should_engage is False
    assert confidence < 0.5


def test_persona_agent_engagement_type(db, sample_user):
    """Test agent engagement type decision"""
    agent = PersonaAgent(sample_user, db, reply_probability=0.5)

    # Test multiple decisions
    engagement_types = [agent.decide_engagement_type() for _ in range(100)]

    # Check variety of engagement types
    assert any(e == EngagementType.LIKE for e in engagement_types)
    assert any(e == EngagementType.REPLY for e in engagement_types)


@pytest.mark.asyncio
async def test_persona_agent_monitor_feed(db, sample_user, sample_tweets):
    """Test agent feed monitoring"""
    agent = PersonaAgent(sample_user, db, reply_probability=0.0)  # No replies for test

    # Monitor feed
    decisions = await agent.monitor_feed(sample_tweets, max_engagements_per_check=2)

    # Should make decisions on relevant tweets
    assert len(decisions) <= 2
    assert all(d.agent_id == sample_user.id for d in decisions)


@pytest.mark.asyncio
async def test_persona_agent_apply_decisions(db, sample_user, sample_tweets):
    """Test applying engagement decisions"""
    agent = PersonaAgent(sample_user, db, reply_probability=0.0)

    # Create mock decision
    from backend.simulation.agentic_loop import AgentDecision

    decision = AgentDecision(
        tweet_id=sample_tweets[0].id,
        agent_id=sample_user.id,
        decision=EngagementType.LIKE,
        confidence=0.8,
        reason="test like",
    )

    # Apply decision
    engagement_ids = agent.apply_decisions([decision])

    # Verify tweet engagement updated
    tweet = db.tweets[sample_tweets[0].id]
    assert tweet.engagement.likes == 101  # Was 100, now 101
    assert len(engagement_ids) == 1


def test_agent_manager_creation(db):
    """Test agent manager initialization"""
    manager = AgentManager(db)

    assert manager.db == db
    assert len(manager.agents) == 0
    assert manager.is_running is False


def test_agent_manager_create_agent(db, sample_user):
    """Test creating agents via manager"""
    manager = AgentManager(db)

    agent = manager.create_agent(sample_user)

    assert agent is not None
    assert manager.get_agent(sample_user.id) == agent
    assert len(manager.get_all_agents()) == 1


def test_agent_manager_stats(db, sample_user):
    """Test agent statistics"""
    manager = AgentManager(db)
    manager.create_agent(sample_user)

    stats = manager.get_agent_stats(sample_user.id)

    assert stats is not None
    assert stats["user_id"] == sample_user.id
    assert stats["total_engagements"] == 0


@pytest.mark.asyncio
async def test_agent_manager_check_cycle(db, sample_user, sample_tweets):
    """Test agent check cycle"""
    manager = AgentManager(db)
    agent = manager.create_agent(sample_user, engagement_threshold=0.5)

    # Run check cycle
    decisions = await manager.agent_check_cycle(agent, max_engagements=2)

    # Should make some decisions
    assert isinstance(decisions, list)


@pytest.mark.asyncio
async def test_agentic_loop_integration(db):
    """Test full agentic loop integration"""
    manager = AgentManager(db)

    # Create multiple agents
    users = [
        User(
            id=f"user-{i}",
            name=f"User {i}",
            persona_type="investor",
            interests=["AI", "Startups"],
            expertise=["Research"],
        )
        for i in range(2)
    ]

    for user in users:
        manager.create_agent(user)

    # Create tweets
    tweets = [
        Tweet(
            id=f"tweet-{i}",
            author_id="author-1",
            content=f"Tweet about AI and startups #{i}",
            topics=["AI", "Startups"],
            engagement=EngagementMetrics(),
            quality_score=0.8,
            created_at=datetime.utcnow(),
        )
        for i in range(3)
    ]

    for tweet in tweets:
        db.add_tweet(tweet)

    # Run agentic loop
    await manager.run_agentic_loop(num_cycles=1)

    # Verify agents made decisions
    for user in users:
        stats = manager.get_agent_stats(user.id)
        assert stats is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
