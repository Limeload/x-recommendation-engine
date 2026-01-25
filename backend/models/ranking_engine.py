"""
Ranking Algorithm Implementation
Multi-stage ranking pipeline with explainability, including exploration-exploitation
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import math
from .schemas import (
    Tweet,
    User,
    RankingExplanation,
    RankedTweet,
    EngagementGraph,
)
from .exploration_ranker import (
    ExplorationRanker,
    ExplorationStrategy,
    ExplorationStats,
)


class RankingEngine:
    """
    Multi-stage ranking engine with tunable weights and exploration-exploitation.
    Stages:
    1. Candidate Generation (In-network & Out-of-network)
    2. Scoring (Heavy Ranker based on X's open-source logic)
    3. Re-Ranking (Diversity & Visibility Filtering)
    4. Exploration (Optional: inject 10% exploratory content)
    """

    def __init__(
        self,
        user: User,
        enable_exploration: bool = True,
        exploration_rate: float = 0.10,
        exploration_strategy: ExplorationStrategy = ExplorationStrategy.EPSILON_GREEDY,
    ):
        """
        Initialize ranking engine for a specific user.

        Args:
            user: User object containing preferences and personalization weights
            enable_exploration: Whether to enable exploration-exploitation (default True)
            exploration_rate: Fraction of feed for exploration (default 0.10 = 10%)
            exploration_strategy: Strategy for exploration (EPSILON_GREEDY, THOMPSON_SAMPLING, UCB)
        """
        self.user = user
        self.weights = user.preference_weights
        self._validate_weights()

        # Initialize exploration layer
        self.enable_exploration = enable_exploration
        self.exploration_ranker = (
            ExplorationRanker(
                exploration_rate=exploration_rate,
                strategy=exploration_strategy,
            )
            if enable_exploration
            else None
        )

    def _validate_weights(self) -> None:
        """Ensure weights sum to approximately 1.0"""
        total = sum(
            self.weights.get(k, 0)
            for k in ["recency", "popularity", "quality", "topic_relevance"]
        )
        if abs(total - 1.0) > 0.01:
            # Normalize weights
            for key in ["recency", "popularity", "quality", "topic_relevance"]:
                if key in self.weights:
                    self.weights[key] = self.weights[key] / total

    def set_weights(self, new_weights: Dict[str, float]) -> None:
        """
        Update ranking weights (for the tuning dashboard).

        Args:
            new_weights: Dictionary with keys like 'recency', 'popularity', etc.
        """
        self.weights.update(new_weights)
        self._validate_weights()

    def rank_tweets(
        self,
        candidates: List[Tweet],
        engagement_graph: Optional[EngagementGraph] = None,
        filter_params: Optional[Dict] = None,
        num_to_return: int = 25,
    ) -> Tuple[List[RankedTweet], Optional[List[Dict]]]:
        """
        Rank tweets for the user using multi-stage pipeline with optional exploration.

        Args:
            candidates: List of candidate tweets to rank
            engagement_graph: User's engagement graph for context
            filter_params: Optional filters (e.g., min_quality, exclude_topics)
            num_to_return: Number of tweets to return (used for exploration layer)

        Returns:
            Tuple of (ranked_tweets, exploration_explanations or None)
        """
        # Stage 1: Filter candidates
        filtered = self._filter_candidates(candidates, filter_params)

        # Stage 2: Score each candidate
        scored_tweets = []
        for tweet in filtered:
            explanation = self._score_tweet(
                tweet, engagement_graph or EngagementGraph(user_id=self.user.user_id)
            )
            scored_tweets.append((tweet, explanation))

        # Stage 3: Sort by total score
        scored_tweets.sort(key=lambda x: x[1].total_score, reverse=True)

        # Stage 4: Apply diversity & re-ranking filters
        reranked = self._apply_diversity_filter(scored_tweets)

        # Stage 5: Assign final ranks
        ranked_tweets = [
            RankedTweet(tweet=tweet, explanation=exp, rank=i + 1)
            for i, (tweet, exp) in enumerate(reranked)
        ]

        # Stage 6: Apply exploration-exploitation if enabled
        exploration_explanations = None
        if self.enable_exploration and self.exploration_ranker:
            ranked_tweets, exploration_explanations = (
                self.exploration_ranker.rerank_with_exploration(
                    ranked_tweets, num_to_return=num_to_return
                )
            )

        return ranked_tweets, exploration_explanations

    def _filter_candidates(
        self, candidates: List[Tweet], filter_params: Optional[Dict] = None
    ) -> List[Tweet]:
        """
        Stage 1: Filter candidates based on rules.

        Args:
            candidates: Initial candidate set
            filter_params: Filtering rules

        Returns:
            Filtered list of tweets
        """
        if not filter_params:
            return candidates

        filtered = candidates.copy()

        # Filter by minimum quality
        if "min_quality" in filter_params:
            min_q = filter_params["min_quality"]
            filtered = [t for t in filtered if t.quality_score >= min_q]

        # Exclude certain topics
        if "exclude_topics" in filter_params:
            exclude = set(filter_params["exclude_topics"])
            filtered = [
                t for t in filtered if not any(topic in exclude for topic in t.topics)
            ]

        # Include only certain topics
        if "include_topics" in filter_params:
            include = set(filter_params["include_topics"])
            filtered = [
                t for t in filtered
                if any(topic in include for topic in t.topics) or len(t.topics) == 0
            ]

        # Exclude certain users
        if "exclude_users" in filter_params:
            exclude_users = set(filter_params["exclude_users"])
            filtered = [t for t in filtered if t.author_id not in exclude_users]

        return filtered

    def _score_tweet(
        self, tweet: Tweet, engagement_graph: EngagementGraph
    ) -> RankingExplanation:
        """
        Stage 2: Score a single tweet using multi-factor ranking.

        Scoring factors:
        1. Recency: Penalize older tweets exponentially
        2. Popularity: Engagement metrics (likes, retweets, replies)
        3. Quality: Content quality signal (author credibility, report score)
        4. Topic Relevance: Match between tweet topics and user interests

        Args:
            tweet: Tweet to score
            engagement_graph: User's engagement context

        Returns:
            RankingExplanation with component scores
        """
        # 1. Recency Score (0-1)
        recency_score = self._calculate_recency_score(tweet)

        # 2. Popularity Score (0-1)
        popularity_score = self._calculate_popularity_score(tweet)

        # 3. Quality Score (0-1) - already in tweet
        quality_score = tweet.quality_score

        # 4. Topic Relevance Score (0-1)
        topic_relevance_score = self._calculate_topic_relevance_score(
            tweet, engagement_graph
        )

        # 5. Diversity Penalty
        diversity_penalty = self._calculate_diversity_penalty(tweet, engagement_graph)

        # Weighted combination
        total_score = (
            self.weights.get("recency", 0.2) * recency_score
            + self.weights.get("popularity", 0.25) * popularity_score
            + self.weights.get("quality", 0.2) * quality_score
            + self.weights.get("topic_relevance", 0.25) * topic_relevance_score
            - self.weights.get("diversity", 0.1) * diversity_penalty
        )

        # Clamp to [0, 1]
        total_score = max(0.0, min(1.0, total_score))

        # Generate key factors for explanation
        key_factors = self._generate_explanation_factors(
            tweet,
            recency_score,
            popularity_score,
            quality_score,
            topic_relevance_score,
            engagement_graph,
        )

        return RankingExplanation(
            tweet_id=tweet.tweet_id,
            total_score=total_score,
            recency_score=recency_score,
            recency_weight=self.weights.get("recency", 0.2),
            popularity_score=popularity_score,
            popularity_weight=self.weights.get("popularity", 0.25),
            quality_score=quality_score,
            quality_weight=self.weights.get("quality", 0.2),
            topic_relevance_score=topic_relevance_score,
            topic_relevance_weight=self.weights.get("topic_relevance", 0.25),
            diversity_penalty=diversity_penalty,
            key_factors=key_factors,
        )

    def _calculate_recency_score(self, tweet: Tweet) -> float:
        """
        Score based on how recent the tweet is.
        Uses exponential decay: score = e^(-k * age_hours)

        Args:
            tweet: Tweet to score

        Returns:
            Score from 0-1
        """
        now = datetime.utcnow()
        age_seconds = max(0, (now - tweet.created_at).total_seconds())
        age_hours = age_seconds / 3600.0

        # Decay constant: half-life of 24 hours
        decay_constant = math.log(2) / 24.0

        score = math.exp(-decay_constant * age_hours)
        return min(1.0, score)

    def _calculate_popularity_score(self, tweet: Tweet) -> float:
        """
        Score based on engagement metrics.
        Uses weighted sum of normalized engagement.

        Args:
            tweet: Tweet to score

        Returns:
            Score from 0-1
        """
        # Normalize engagement with reasonable maximums
        max_likes = 10000
        max_retweets = 2000
        max_replies = 500
        max_bookmarks = 1000

        normalized_likes = min(1.0, tweet.likes / max_likes)
        normalized_retweets = min(1.0, tweet.retweets / max_retweets)
        normalized_replies = min(1.0, tweet.replies / max_replies)
        normalized_bookmarks = min(1.0, tweet.bookmarks / max_bookmarks)

        # Weighted engagement (typical X weighting)
        popularity_score = (
            0.4 * normalized_likes
            + 0.35 * normalized_retweets
            + 0.15 * normalized_replies
            + 0.1 * normalized_bookmarks
        )

        return min(1.0, popularity_score)

    def _calculate_topic_relevance_score(
        self, tweet: Tweet, engagement_graph: EngagementGraph
    ) -> float:
        """
        Score based on match between tweet topics and user interests.

        Args:
            tweet: Tweet to score
            engagement_graph: User's engagement context

        Returns:
            Score from 0-1
        """
        user_interests = set(self.user.interests)
        user_expertise = set(self.user.expertise_areas)
        tweet_topics = set(tweet.topics)

        if not tweet_topics or not user_interests:
            return 0.5  # Neutral score if no topics

        # Calculate Jaccard similarity
        intersection = user_interests.intersection(tweet_topics)
        union = user_interests.union(tweet_topics)

        jaccard = len(intersection) / len(union) if union else 0.0

        # Also consider expertise areas with higher weight
        expertise_match = len(user_expertise.intersection(tweet_topics)) / max(
            len(user_expertise), 1
        )

        # Combine: 60% Jaccard, 40% expertise match
        relevance_score = 0.6 * jaccard + 0.4 * expertise_match

        return min(1.0, relevance_score)

    def _calculate_diversity_penalty(
        self, tweet: Tweet, engagement_graph: EngagementGraph
    ) -> float:
        """
        Calculate penalty to avoid cluster/redundancy.
        Penalizes tweets from same author or about same topic.

        Args:
            tweet: Tweet to score
            engagement_graph: User's engagement context

        Returns:
            Penalty from 0-1
        """
        # Simple implementation: penalize if author is not followed
        if engagement_graph and tweet.author_id in engagement_graph.following:
            return 0.0  # No penalty for followed users

        # Penalize unknown authors slightly
        return 0.05

    def _apply_diversity_filter(
        self, scored_tweets: List[Tuple[Tweet, RankingExplanation]]
    ) -> List[Tuple[Tweet, RankingExplanation]]:
        """
        Stage 4: Apply diversity/visibility filtering.
        Ensure we don't have too many tweets from same author or topic.

        Args:
            scored_tweets: List of (tweet, explanation) tuples sorted by score

        Returns:
            Re-ranked list with diversity applied
        """
        result = []
        author_count: Dict[str, int] = {}
        topic_count: Dict[str, int] = {}

        max_per_author = 3
        max_per_topic = 5

        for tweet, explanation in scored_tweets:
            # Check author diversity
            if author_count.get(tweet.author_id, 0) >= max_per_author:
                continue

            # Check topic diversity
            tweet_topics = set(tweet.topics)
            skip = False
            for topic in tweet_topics:
                if topic_count.get(topic, 0) >= max_per_topic:
                    skip = True
                    break

            if skip:
                continue

            result.append((tweet, explanation))
            author_count[tweet.author_id] = author_count.get(tweet.author_id, 0) + 1
            for topic in tweet_topics:
                topic_count[topic] = topic_count.get(topic, 0) + 1

        return result

    def _generate_explanation_factors(
        self,
        tweet: Tweet,
        recency_score: float,
        popularity_score: float,
        quality_score: float,
        topic_relevance_score: float,
        engagement_graph: EngagementGraph,
    ) -> List[str]:
        """
        Generate human-readable explanation factors.

        Args:
            tweet: Tweet being explained
            recency_score: Recency component score
            popularity_score: Popularity component score
            quality_score: Quality component score
            topic_relevance_score: Topic relevance component score
            engagement_graph: User's engagement context

        Returns:
            List of explanation strings
        """
        factors = []

        # Recency
        if recency_score > 0.8:
            factors.append("Very recent and fresh content")
        elif recency_score > 0.5:
            factors.append("Recent content")

        # Popularity
        if popularity_score > 0.8:
            factors.append("Highly engaging content (high likes/retweets)")
        elif popularity_score > 0.5:
            factors.append("Well-engaged content")

        # Quality
        if quality_score > 0.8:
            factors.append("High content quality signal")
        elif quality_score > 0.6:
            factors.append("Good content quality")

        # Topic relevance
        if topic_relevance_score > 0.8:
            factors.append(f"Strong match to your interests: {', '.join(tweet.topics)}")
        elif topic_relevance_score > 0.5:
            factors.append(f"Relevant to your interests: {', '.join(tweet.topics)}")

        # Author context
        if engagement_graph and tweet.author_id in engagement_graph.following:
            factors.append("From an account you follow")

        # Engagement context
        if tweet.in_reply_to_user_id == self.user.user_id:
            factors.append("Reply to your tweet")
        elif tweet.mentions and self.user.username in tweet.mentions:
            factors.append("Mentions your account")

        return factors if factors else ["Balanced content recommendation"]
    # ========== EXPLORATION-EXPLOITATION METHODS ==========

    def record_engagement_for_exploration(
        self,
        tweet_id: str,
        author_id: str,
        engagement_type: str = "view",
    ) -> None:
        """
        Record engagement feedback to update exploration statistics.
        Should be called when user interacts with a tweet from the feed.

        Args:
            tweet_id: ID of the tweet
            author_id: ID of the author
            engagement_type: Type of engagement (view, like, reply, retweet, bookmark)
        """
        if not self.exploration_ranker:
            return

        was_engaged = engagement_type in ["like", "reply", "retweet", "bookmark"]
        self.exploration_ranker.record_engagement(
            tweet_id=tweet_id,
            author_id=author_id,
            was_engaged=was_engaged,
            engagement_type=engagement_type,
        )

    def get_exploration_stats(self) -> Optional[Dict]:
        """
        Get exploration statistics and insights.

        Returns:
            Dictionary with exploration metrics, or None if exploration disabled
        """
        if not self.exploration_ranker:
            return None

        return self.exploration_ranker.get_exploration_stats()

    def set_exploration_rate(self, rate: float) -> None:
        """
        Dynamically adjust exploration rate during runtime.

        Args:
            rate: New exploration rate (0-1)
        """
        if not self.exploration_ranker:
            raise ValueError("Exploration is not enabled for this ranking engine")

        if not (0.0 <= rate <= 1.0):
            raise ValueError(f"Exploration rate must be in [0, 1], got {rate}")

        self.exploration_ranker.exploration_rate = rate

    def set_exploration_strategy(self, strategy: ExplorationStrategy) -> None:
        """
        Change exploration strategy at runtime.

        Args:
            strategy: New strategy (EPSILON_GREEDY, THOMPSON_SAMPLING, or UCB)
        """
        if not self.exploration_ranker:
            raise ValueError("Exploration is not enabled for this ranking engine")

        self.exploration_ranker.strategy = strategy

    def reset_exploration_stats(self) -> None:
        """
        Clear all exploration history and statistics.
        Useful for resetting the exploration phase.
        """
        if self.exploration_ranker:
            self.exploration_ranker.reset_stats()
