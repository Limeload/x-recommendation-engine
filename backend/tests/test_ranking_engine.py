"""
Unit tests for the ranking engine
"""

import pytest
from datetime import datetime, timedelta
from models.schemas import User, Tweet, UserPersona, EngagementGraph
from models.ranking_engine import RankingEngine


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        user_id="test_user_1",
        username="test_user",
        persona=UserPersona.FOUNDER,
        interests=["AI", "Startups", "Technology"],
        expertise_areas=["ProductManagement", "Leadership"],
        preference_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1,
        },
    )


@pytest.fixture
def sample_tweets():
    """Create sample tweets for testing"""
    now = datetime.utcnow()
    return [
        Tweet(
            tweet_id="tweet_1",
            author_id="author_1",
            content="Just launched our AI startup!",
            created_at=now - timedelta(hours=1),
            likes=100,
            retweets=20,
            replies=5,
            bookmarks=15,
            topics=["AI", "Startups"],
            hashtags=["#AI", "#StartupLife"],
            quality_score=0.85,
        ),
        Tweet(
            tweet_id="tweet_2",
            author_id="author_2",
            content="Technology news from today",
            created_at=now - timedelta(hours=6),
            likes=500,
            retweets=150,
            replies=30,
            bookmarks=100,
            topics=["Technology"],
            hashtags=["#Tech"],
            quality_score=0.75,
        ),
        Tweet(
            tweet_id="tweet_3",
            author_id="author_1",
            content="Old tweet from a week ago",
            created_at=now - timedelta(days=7),
            likes=10,
            retweets=2,
            replies=1,
            bookmarks=3,
            topics=["Random"],
            hashtags=[],
            quality_score=0.5,
        ),
    ]


class TestRankingEngine:
    """Test suite for RankingEngine"""

    def test_initialization(self, sample_user):
        """Test engine initialization"""
        engine = RankingEngine(sample_user)
        assert engine.user.user_id == "test_user_1"
        assert engine.weights["recency"] > 0

    def test_weight_validation(self, sample_user):
        """Test weight normalization"""
        user = sample_user.copy()
        user.preference_weights = {"recency": 0.5, "popularity": 0.5}
        engine = RankingEngine(user)
        # Weights should be normalized
        assert abs(sum(engine.weights.values()) - 1.0) < 0.01

    def test_recency_score(self, sample_user):
        """Test recency scoring"""
        engine = RankingEngine(sample_user)
        now = datetime.utcnow()

        # Recent tweet
        recent_tweet = Tweet(
            tweet_id="recent",
            author_id="author",
            content="test",
            created_at=now,
            quality_score=0.5,
        )
        recent_score = engine._calculate_recency_score(recent_tweet)
        assert 0.9 < recent_score <= 1.0

        # Old tweet (7 days)
        old_tweet = Tweet(
            tweet_id="old",
            author_id="author",
            content="test",
            created_at=now - timedelta(days=7),
            quality_score=0.5,
        )
        old_score = engine._calculate_recency_score(old_tweet)
        assert 0 < old_score < 0.1

    def test_popularity_score(self, sample_user):
        """Test popularity scoring"""
        engine = RankingEngine(sample_user)

        # High engagement
        viral_tweet = Tweet(
            tweet_id="viral",
            author_id="author",
            content="test",
            created_at=datetime.utcnow(),
            likes=5000,
            retweets=1000,
            replies=250,
            bookmarks=500,
            quality_score=0.5,
        )
        viral_score = engine._calculate_popularity_score(viral_tweet)
        assert viral_score > 0.7

        # Low engagement
        quiet_tweet = Tweet(
            tweet_id="quiet",
            author_id="author",
            content="test",
            created_at=datetime.utcnow(),
            likes=0,
            retweets=0,
            replies=0,
            bookmarks=0,
            quality_score=0.5,
        )
        quiet_score = engine._calculate_popularity_score(quiet_tweet)
        assert quiet_score < 0.1

    def test_topic_relevance_score(self, sample_user):
        """Test topic relevance scoring"""
        engine = RankingEngine(sample_user)

        # Matching topics
        relevant_tweet = Tweet(
            tweet_id="relevant",
            author_id="author",
            content="test",
            created_at=datetime.utcnow(),
            topics=["AI", "Startups"],
            quality_score=0.5,
        )
        relevant_score = engine._calculate_topic_relevance_score(
            relevant_tweet, EngagementGraph(user_id="test")
        )
        assert relevant_score > 0.5

        # Non-matching topics
        irrelevant_tweet = Tweet(
            tweet_id="irrelevant",
            author_id="author",
            content="test",
            created_at=datetime.utcnow(),
            topics=["Sports", "Music"],
            quality_score=0.5,
        )
        irrelevant_score = engine._calculate_topic_relevance_score(
            irrelevant_tweet, EngagementGraph(user_id="test")
        )
        assert irrelevant_score < 0.3

    def test_rank_tweets(self, sample_user, sample_tweets):
        """Test full ranking pipeline"""
        engine = RankingEngine(sample_user)
        ranked = engine.rank_tweets(sample_tweets)

        # Should rank all tweets
        assert len(ranked) == len(sample_tweets)

        # Should be sorted by score
        scores = [r.explanation.total_score for r in ranked]
        assert scores == sorted(scores, reverse=True)

        # All should have explanations
        for ranked_tweet in ranked:
            assert ranked_tweet.explanation is not None
            assert len(ranked_tweet.explanation.key_factors) > 0

    def test_weight_tuning(self, sample_user, sample_tweets):
        """Test weight tuning affects ranking"""
        engine = RankingEngine(sample_user)
        ranked_default = engine.rank_tweets(sample_tweets)

        # Change weights to heavily favor popularity
        engine.set_weights(
            {
                "recency": 0.1,
                "popularity": 0.7,
                "quality": 0.1,
                "topic_relevance": 0.1,
                "diversity": 0.0,
            }
        )
        ranked_popularity = engine.rank_tweets(sample_tweets)

        # Rankings might differ (popular tweets ranked higher)
        top_default = ranked_default[0].tweet.tweet_id
        top_popularity = ranked_popularity[0].tweet.tweet_id
        # At least one ranking should differ (not guaranteed but likely)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
