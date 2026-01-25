"""
Test suite for Exploration-Exploitation layer
Tests Thompson Sampling, Epsilon-Greedy, and UCB strategies
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from backend.models.schemas import Tweet, User, EngagementMetrics, RankingExplanation, RankedTweet
from backend.models.exploration_ranker import (
    ExplorationRanker,
    ExplorationStrategy,
    ExplorationStats,
)
from backend.models.ranking_engine import RankingEngine


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        id="user-1",
        username="testuser",
        name="Test User",
        interests=["AI", "Startups"],
        expertise_areas=["Data Science"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
        },
    )


@pytest.fixture
def sample_tweets():
    """Create sample tweets for ranking"""
    tweets = []
    authors = ["author-1", "author-2", "author-3", "author-4", "author-5"]

    for i, author in enumerate(authors):
        tweet = Tweet(
            tweet_id=f"tweet-{i+1}",
            author_id=author,
            content=f"Sample tweet {i+1}",
            topics=["AI", "Tech"] if i < 3 else ["Sports", "News"],
            engagement=EngagementMetrics(
                likes=100 + i * 50,
                retweets=20 + i * 10,
                replies=5 + i * 2,
            ),
            quality_score=0.7 + i * 0.05,
            created_at=datetime.utcnow() - timedelta(hours=i),
        )
        tweets.append(tweet)

    return tweets


class TestExplorationStats:
    """Test ExplorationStats class"""

    def test_initialization(self):
        """Test stats initialization"""
        stats = ExplorationStats(successes=5, failures=3)
        assert stats.successes == 5
        assert stats.failures == 3
        assert stats.total_trials == 8

    def test_empirical_rate(self):
        """Test empirical engagement rate calculation"""
        stats = ExplorationStats(successes=7, failures=3)
        assert stats.empirical_rate == 0.7

    def test_empirical_rate_uninformed(self):
        """Test empirical rate with no data"""
        stats = ExplorationStats(successes=0, failures=0)
        assert stats.empirical_rate == 0.5  # Neutral prior

    def test_thompson_sample_shape(self):
        """Test Thompson sampling produces valid probabilities"""
        stats = ExplorationStats(successes=10, failures=5)

        samples = [stats.thompson_sample() for _ in range(100)]

        assert all(0 <= s <= 1 for s in samples), "All samples should be in [0, 1]"
        assert np.mean(samples) > 0.5, "Average should be > 0.5 with more successes"

    def test_thompson_sample_with_no_data(self):
        """Test Thompson sampling with uninformed prior"""
        stats = ExplorationStats(successes=0, failures=0)

        # With uninformed prior, samples should be wide
        samples = [stats.thompson_sample() for _ in range(100)]
        assert np.std(samples) > 0.25, "Should have high variance with no data"

    def test_ucb_score_basic(self):
        """Test UCB score calculation"""
        stats = ExplorationStats(successes=8, failures=2)
        ucb = stats.ucb_score(c=1.0)

        # Should be at least empirical rate
        assert ucb >= stats.empirical_rate
        # Should be less than 1
        assert ucb <= 1.0

    def test_ucb_score_explores_unknowns(self):
        """Test that UCB gives higher scores to unexplored items"""
        known = ExplorationStats(successes=100, failures=100)  # Well-explored
        unknown = ExplorationStats(successes=0, failures=0)     # Never explored

        known_ucb = known.ucb_score(c=1.25)
        unknown_ucb = unknown.ucb_score(c=1.25)

        # Unknown should get higher UCB despite lower empirical rate
        assert unknown_ucb > known_ucb


class TestEpsilonGreedy:
    """Test Epsilon-Greedy strategy"""

    def test_epsilon_greedy_selection(self):
        """Test epsilon-greedy selects random items"""
        ranker = ExplorationRanker(
            exploration_rate=0.5,
            strategy=ExplorationStrategy.EPSILON_GREEDY,
        )

        # Create 20 dummy tweets
        tweets = [
            RankedTweet(
                tweet=Tweet(
                    tweet_id=f"tweet-{i}",
                    author_id=f"author-{i}",
                    content=f"Tweet {i}",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.9 - i * 0.01,
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id=f"tweet-{i}",
                    total_score=0.9 - i * 0.01,
                ),
                rank=i + 1,
            )
            for i in range(20)
        ]

        # Request 10 tweets with 50% exploration
        result, explanations = ranker.rerank_with_exploration(tweets, num_to_return=10)

        assert len(result) == 10
        assert len(explanations) == 10

        # Count how many are exploration vs exploitation
        exploration_count = sum(
            1 for exp in explanations if exp["selected_for"] == "exploration"
        )
        # Should be roughly 50%
        assert 3 <= exploration_count <= 7

    def test_epsilon_greedy_deterministic_with_small_pool(self):
        """Test epsilon-greedy with pool smaller than request"""
        ranker = ExplorationRanker(
            exploration_rate=0.5,
            strategy=ExplorationStrategy.EPSILON_GREEDY,
        )

        # Only 5 tweets, request 10
        tweets = [
            RankedTweet(
                tweet=Tweet(
                    tweet_id=f"tweet-{i}",
                    author_id=f"author-{i}",
                    content=f"Tweet {i}",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.9,
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id=f"tweet-{i}",
                    total_score=0.9,
                ),
                rank=i + 1,
            )
            for i in range(5)
        ]

        result, explanations = ranker.rerank_with_exploration(tweets, num_to_return=10)

        # Should return all 5
        assert len(result) == 5


class TestThompsonSampling:
    """Test Thompson Sampling strategy"""

    def test_thompson_sampling_selection(self, sample_tweets):
        """Test Thompson sampling-based selection"""
        ranker = ExplorationRanker(
            exploration_rate=0.3,
            strategy=ExplorationStrategy.THOMPSON_SAMPLING,
        )

        # Create ranking explanations
        ranked_tweets = [
            RankedTweet(
                tweet=tweet,
                explanation=RankingExplanation(
                    tweet_id=tweet.tweet_id,
                    total_score=0.5 + i * 0.1,
                ),
                rank=i + 1,
            )
            for i, tweet in enumerate(sample_tweets)
        ]

        # Add some engagement history
        ranker.stats["author_author-1"] = ExplorationStats(successes=20, failures=5)
        ranker.stats["author_author-2"] = ExplorationStats(successes=5, failures=10)

        result, explanations = ranker.rerank_with_exploration(ranked_tweets, num_to_return=5)

        assert len(result) == 5
        assert len(explanations) == 5

        # Verify explanations contain stats
        for exp in explanations:
            assert "author_stats" in exp

    def test_thompson_sampling_uncertainty_bonus(self):
        """Test that Thompson sampling gives bonus to uncertain items"""
        ranker = ExplorationRanker(
            exploration_rate=0.5,
            strategy=ExplorationStrategy.THOMPSON_SAMPLING,
        )

        # One author with high engagement, well-known
        known_author = "author-known"
        ranker.stats[f"author_{known_author}"] = ExplorationStats(
            successes=100, failures=10
        )

        # One author with unknown engagement
        unknown_author = "author-unknown"
        ranker.stats[f"author_{unknown_author}"] = ExplorationStats(
            successes=0, failures=0
        )

        # Select from these two
        tweets = [
            RankedTweet(
                tweet=Tweet(
                    tweet_id="t1",
                    author_id=known_author,
                    content="Known",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.9,
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id="t1", total_score=0.9
                ),
                rank=1,
            ),
            RankedTweet(
                tweet=Tweet(
                    tweet_id="t2",
                    author_id=unknown_author,
                    content="Unknown",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.5,
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id="t2", total_score=0.5
                ),
                rank=2,
            ),
        ]

        # Run multiple times to check variance
        selections = []
        for _ in range(10):
            result, _ = ranker.rerank_with_exploration(tweets, num_to_return=1)
            selections.append(result[0].tweet.tweet_id)

        # Unknown should be selected sometimes despite lower quality
        unknown_selected = sum(1 for s in selections if s == "t2")
        assert unknown_selected > 0, "Unknown author should be explored sometimes"


class TestUCB:
    """Test Upper Confidence Bound strategy"""

    def test_ucb_selection(self, sample_tweets):
        """Test UCB-based selection"""
        ranker = ExplorationRanker(
            exploration_rate=0.3,
            strategy=ExplorationStrategy.UCB,
        )

        ranked_tweets = [
            RankedTweet(
                tweet=tweet,
                explanation=RankingExplanation(
                    tweet_id=tweet.tweet_id,
                    total_score=0.5 + i * 0.1,
                ),
                rank=i + 1,
            )
            for i, tweet in enumerate(sample_tweets)
        ]

        result, explanations = ranker.rerank_with_exploration(ranked_tweets, num_to_return=5)

        assert len(result) == 5
        assert all("reason" in exp for exp in explanations)

    def test_ucb_explores_uncertain(self):
        """Test that UCB explores high-uncertainty items"""
        ranker = ExplorationRanker(
            exploration_rate=0.5,
            strategy=ExplorationStrategy.UCB,
        )

        # Low engagement, high certainty (bad item)
        bad_author = "author-bad"
        ranker.stats[f"author_{bad_author}"] = ExplorationStats(
            successes=1, failures=100
        )

        # Unknown author
        unknown_author = "author-unknown"
        # (No stats = highest UCB bonus)

        tweets = [
            RankedTweet(
                tweet=Tweet(
                    tweet_id="t1",
                    author_id=bad_author,
                    content="Bad",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.95,  # High original score
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id="t1", total_score=0.95
                ),
                rank=1,
            ),
            RankedTweet(
                tweet=Tweet(
                    tweet_id="t2",
                    author_id=unknown_author,
                    content="Unknown",
                    topics=["Test"],
                    engagement=EngagementMetrics(),
                    quality_score=0.5,
                    created_at=datetime.utcnow(),
                ),
                explanation=RankingExplanation(
                    tweet_id="t2", total_score=0.5
                ),
                rank=2,
            ),
        ]

        # Run multiple times
        selections = []
        for _ in range(10):
            result, _ = ranker.rerank_with_exploration(tweets, num_to_return=1)
            selections.append(result[0].tweet.tweet_id)

        # Unknown should be selected despite lower quality
        unknown_selected = sum(1 for s in selections if s == "t2")
        assert unknown_selected > 3, f"Unknown should be selected often, got {unknown_selected}/10"


class TestEngagementRecording:
    """Test engagement feedback recording"""

    def test_record_engagement_success(self):
        """Test recording successful engagement"""
        ranker = ExplorationRanker(exploration_rate=0.1)

        ranker.record_engagement(
            tweet_id="tweet-1",
            author_id="author-1",
            was_engaged=True,
            engagement_type="like",
        )

        assert "author_author-1" in ranker.stats
        assert ranker.stats["author_author-1"].successes == 1
        assert ranker.stats["author_author-1"].failures == 0

    def test_record_engagement_failure(self):
        """Test recording unsuccessful engagement"""
        ranker = ExplorationRanker(exploration_rate=0.1)

        ranker.record_engagement(
            tweet_id="tweet-1",
            author_id="author-1",
            was_engaged=False,
            engagement_type="view",
        )

        assert ranker.stats["author_author-1"].successes == 0
        assert ranker.stats["author_author-1"].failures == 1

    def test_engagement_history_tracking(self):
        """Test that engagement is tracked in history"""
        ranker = ExplorationRanker(exploration_rate=0.1)

        ranker.record_engagement("tweet-1", "author-1", True, "like")
        ranker.record_engagement("tweet-2", "author-2", False, "view")

        assert len(ranker.exploration_history) == 2
        assert ranker.exploration_history[0]["tweet_id"] == "tweet-1"
        assert ranker.exploration_history[0]["engaged"] is True
        assert ranker.exploration_history[1]["engagement_type"] == "view"


class TestRankingEngineIntegration:
    """Test integration with RankingEngine"""

    def test_ranking_engine_with_exploration(self, sample_user, sample_tweets):
        """Test RankingEngine with exploration enabled"""
        engine = RankingEngine(
            user=sample_user,
            enable_exploration=True,
            exploration_rate=0.2,
        )

        ranked, explanations = engine.rank_tweets(
            candidates=sample_tweets,
            num_to_return=4,
        )

        assert len(ranked) == 4
        assert len(explanations) == 4

        # Check that we have both exploitation and exploration
        types = [exp["selected_for"] for exp in explanations]
        assert "exploitation" in types
        assert "exploration" in types

    def test_ranking_engine_exploration_disabled(self, sample_user, sample_tweets):
        """Test RankingEngine with exploration disabled"""
        engine = RankingEngine(
            user=sample_user,
            enable_exploration=False,
        )

        ranked, explanations = engine.rank_tweets(
            candidates=sample_tweets,
            num_to_return=4,
        )

        assert len(ranked) == 4
        assert explanations is None

    def test_record_engagement_integration(self, sample_user, sample_tweets):
        """Test recording engagement through RankingEngine"""
        engine = RankingEngine(
            user=sample_user,
            enable_exploration=True,
        )

        engine.record_engagement_for_exploration(
            tweet_id="tweet-1",
            author_id="author-1",
            engagement_type="like",
        )

        stats = engine.get_exploration_stats()
        assert stats["total_authors_tracked"] == 1

    def test_dynamic_exploration_adjustment(self, sample_user):
        """Test adjusting exploration settings at runtime"""
        engine = RankingEngine(
            user=sample_user,
            enable_exploration=True,
            exploration_rate=0.1,
        )

        # Change rate
        engine.set_exploration_rate(0.2)
        assert engine.exploration_ranker.exploration_rate == 0.2

        # Change strategy
        engine.set_exploration_strategy(ExplorationStrategy.THOMPSON_SAMPLING)
        assert engine.exploration_ranker.strategy == ExplorationStrategy.THOMPSON_SAMPLING

    def test_exploration_stats_retrieval(self, sample_user, sample_tweets):
        """Test retrieving exploration statistics"""
        engine = RankingEngine(
            user=sample_user,
            enable_exploration=True,
        )

        # Record some engagements
        engine.record_engagement_for_exploration("tweet-1", "author-1", "like")
        engine.record_engagement_for_exploration("tweet-2", "author-1", "like")
        engine.record_engagement_for_exploration("tweet-3", "author-2", "view")

        stats = engine.get_exploration_stats()

        assert stats["total_authors_tracked"] == 2
        assert stats["strategy_used"] == "epsilon_greedy"
        assert stats["average_engagement_rate"] > 0.3


class TestExplorationEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_exploration_rate(self):
        """Test validation of exploration rate"""
        with pytest.raises(ValueError):
            ExplorationRanker(exploration_rate=1.5)

        with pytest.raises(ValueError):
            ExplorationRanker(exploration_rate=-0.1)

    def test_empty_ranked_list(self):
        """Test with empty tweet list"""
        ranker = ExplorationRanker(exploration_rate=0.1)
        result, explanations = ranker.rerank_with_exploration([], num_to_return=10)

        assert result == []
        assert explanations == []

    def test_reset_stats(self):
        """Test resetting exploration statistics"""
        ranker = ExplorationRanker(exploration_rate=0.1)

        ranker.record_engagement("tweet-1", "author-1", True)
        assert len(ranker.stats) > 0
        assert len(ranker.exploration_history) > 0

        ranker.reset_stats()

        assert len(ranker.stats) == 0
        assert len(ranker.exploration_history) == 0

    def test_duplicate_author_stats(self):
        """Test that multiple engagements from same author are tracked correctly"""
        ranker = ExplorationRanker(exploration_rate=0.1)

        ranker.record_engagement("tweet-1", "author-1", True)
        ranker.record_engagement("tweet-2", "author-1", True)
        ranker.record_engagement("tweet-3", "author-1", False)

        stats = ranker.stats["author_author-1"]
        assert stats.successes == 2
        assert stats.failures == 1
        assert stats.total_trials == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
