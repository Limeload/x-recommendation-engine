"""
Exploration-Exploitation Layer for Feed Re-ranking
Implements Thompson Sampling and Epsilon-Greedy strategies to inject exploratory content
into the feed, balancing exploitation of known good content with exploration of new/diverse content.
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict
import random
import math
from datetime import datetime, timedelta
from scipy import stats
import numpy as np

from .schemas import Tweet, RankedTweet, RankingExplanation


class ExplorationStrategy(str, Enum):
    """Exploration strategies for balancing exploitation vs exploration"""

    EPSILON_GREEDY = "epsilon_greedy"  # Simple: explore with fixed probability
    THOMPSON_SAMPLING = "thompson_sampling"  # Bayesian: explore based on uncertainty
    UCB = "ucb"  # Upper Confidence Bound: explore high-uncertainty, high-potential items


class ExplorationStats(dict):
    """Statistics for exploration tracking per tweet/author"""

    def __init__(self, successes: int = 0, failures: int = 0):
        super().__init__()
        self.successes = successes
        self.failures = failures

    @property
    def total_trials(self) -> int:
        """Total number of exposures"""
        return self.successes + self.failures

    @property
    def empirical_rate(self) -> float:
        """Empirical engagement rate"""
        if self.total_trials == 0:
            return 0.5  # Neutral prior
        return self.successes / self.total_trials

    def thompson_sample(self, alpha: float = 1.0, beta: float = 1.0) -> float:
        """
        Sample from Beta distribution representing engagement probability.

        Thompson Sampling uses the Beta-Bernoulli conjugate pair for engagement.
        Args:
            alpha: Prior successes (default 1.0 for uninformed)
            beta: Prior failures (default 1.0 for uninformed)

        Returns:
            Sampled engagement probability (0-1)
        """
        # Posterior parameters
        alpha_post = alpha + self.successes
        beta_post = beta + self.failures

        # Sample from posterior Beta distribution
        return float(np.random.beta(alpha_post, beta_post))

    def ucb_score(self, c: float = 1.25) -> float:
        """
        Upper Confidence Bound score for optimistic exploration.

        Args:
            c: Exploration constant (higher = more exploration)

        Returns:
            UCB score combining empirical rate + uncertainty bonus
        """
        if self.total_trials == 0:
            return 1.0  # Unknown items get maximum UCB

        # Empirical rate + confidence bonus
        confidence_bonus = c * math.sqrt(math.log(max(1, self.total_trials)) / self.total_trials)
        return min(1.0, self.empirical_rate + confidence_bonus)


class ExplorationRanker:
    """
    Exploration-Exploitation layer for feed re-ranking.
    Injects exploratory content while maintaining exploitation of good content.
    """

    def __init__(
        self,
        exploration_rate: float = 0.10,
        strategy: ExplorationStrategy = ExplorationStrategy.EPSILON_GREEDY,
        historical_stats: Optional[Dict[str, ExplorationStats]] = None,
    ):
        """
        Initialize exploration ranker.

        Args:
            exploration_rate: Fraction of feed to explore (0-1). Default 0.10 for 10%
            strategy: Exploration strategy to use (EPSILON_GREEDY, THOMPSON_SAMPLING, UCB)
            historical_stats: Optional historical engagement stats per tweet/author
        """
        if not (0.0 <= exploration_rate <= 1.0):
            raise ValueError(f"exploration_rate must be in [0, 1], got {exploration_rate}")

        self.exploration_rate = exploration_rate
        self.strategy = strategy
        self.stats: Dict[str, ExplorationStats] = historical_stats or {}
        self.exploration_history: List[Dict] = []  # Track what was explored

    def rerank_with_exploration(
        self,
        ranked_tweets: List[RankedTweet],
        num_to_return: int = 25,
    ) -> Tuple[List[RankedTweet], List[Dict]]:
        """
        Apply exploration-exploitation re-ranking to feed.

        This modifies the ranking to inject exploratory content while maintaining
        the quality of top recommendations.

        Args:
            ranked_tweets: Already-ranked tweets from base ranker
            num_to_return: Number of tweets to return in final feed

        Returns:
            Tuple of (reranked_tweets, exploration_explanations)
        """
        if not ranked_tweets:
            return [], []

        if len(ranked_tweets) <= num_to_return:
            # No exploration needed if we're returning all available
            return ranked_tweets[:num_to_return], []

        # Determine how many slots for exploration
        num_exploration = max(1, int(num_to_return * self.exploration_rate))
        num_exploitation = num_to_return - num_exploration

        # Split into exploitation and exploration pools
        exploitation_tweets = ranked_tweets[:num_exploitation]
        exploration_pool = ranked_tweets[num_exploitation:]

        # Select exploratory tweets
        exploration_tweets = self._select_exploration_candidates(
            exploration_pool, num_exploration
        )

        # Combine and shuffle to avoid obvious pattern
        combined = exploitation_tweets + exploration_tweets
        random.shuffle(combined)

        # Record exploration data
        explanations = [
            self._create_exploration_explanation(tweet, is_exploration=tweet in exploration_tweets)
            for tweet in combined
        ]

        return combined, explanations

    def _select_exploration_candidates(
        self,
        candidates: List[RankedTweet],
        num_to_select: int,
    ) -> List[RankedTweet]:
        """
        Select candidates for exploration using the configured strategy.

        Args:
            candidates: Pool of candidates to explore
            num_to_select: Number to select

        Returns:
            Selected candidates for exploration
        """
        if self.strategy == ExplorationStrategy.EPSILON_GREEDY:
            return self._epsilon_greedy_selection(candidates, num_to_select)
        elif self.strategy == ExplorationStrategy.THOMPSON_SAMPLING:
            return self._thompson_sampling_selection(candidates, num_to_select)
        elif self.strategy == ExplorationStrategy.UCB:
            return self._ucb_selection(candidates, num_to_select)
        else:
            return candidates[:num_to_select]

    def _epsilon_greedy_selection(
        self,
        candidates: List[RankedTweet],
        num_to_select: int,
    ) -> List[RankedTweet]:
        """
        Epsilon-Greedy: Randomly select from exploration pool.
        Simple but effective: ignore ranking scores, just pick random items.

        Args:
            candidates: Pool of candidates
            num_to_select: Number to select

        Returns:
            Randomly selected candidates
        """
        selected = random.sample(
            candidates, min(num_to_select, len(candidates))
        )
        return selected

    def _thompson_sampling_selection(
        self,
        candidates: List[RankedTweet],
        num_to_select: int,
    ) -> List[RankedTweet]:
        """
        Thompson Sampling: Score each candidate by sampling from its engagement distribution.
        Candidates with more uncertainty are preferred for exploration.

        Args:
            candidates: Pool of candidates
            num_to_select: Number to select

        Returns:
            Candidates selected via Thompson Sampling
        """
        # Score each candidate
        scored = []
        for tweet in candidates:
            stat_key = f"author_{tweet.tweet.author_id}"
            stats_obj = self.stats.get(stat_key, ExplorationStats())

            # Thompson sample: get sampled engagement probability
            sampled_engagement = stats_obj.thompson_sample()

            # Combine with author-level signal
            final_score = (
                0.6 * sampled_engagement +  # Thompson sample
                0.4 * tweet.explanation.total_score  # Original ranker score
            )

            scored.append((tweet, final_score))

        # Sort by Thompson-sampled scores and take top
        scored.sort(key=lambda x: x[1], reverse=True)
        return [tweet for tweet, _ in scored[:num_to_select]]

    def _ucb_selection(
        self,
        candidates: List[RankedTweet],
        num_to_select: int,
    ) -> List[RankedTweet]:
        """
        Upper Confidence Bound: Prefer high-potential, high-uncertainty items.
        Items with few exposures but good historical performance get boosted.

        Args:
            candidates: Pool of candidates
            num_to_select: Number to select

        Returns:
            Candidates selected via UCB
        """
        # Score each candidate with UCB
        scored = []
        for tweet in candidates:
            stat_key = f"author_{tweet.tweet.author_id}"
            stats_obj = self.stats.get(stat_key, ExplorationStats())

            # UCB score: empirical rate + confidence bonus
            ucb_score = stats_obj.ucb_score(c=1.25)

            # Combine with original score (weighted toward UCB for exploration)
            final_score = (
                0.7 * ucb_score +  # UCB score (high exploration bonus)
                0.3 * tweet.explanation.total_score  # Original ranker score
            )

            scored.append((tweet, final_score))

        # Sort by UCB scores and take top
        scored.sort(key=lambda x: x[1], reverse=True)
        return [tweet for tweet, _ in scored[:num_to_select]]

    def record_engagement(
        self,
        tweet_id: str,
        author_id: str,
        was_engaged: bool,
        engagement_type: str = "view",
    ) -> None:
        """
        Record engagement feedback to update exploration statistics.

        Args:
            tweet_id: ID of the tweet shown
            author_id: ID of the author
            was_engaged: Whether user engaged (liked, replied, etc.)
            engagement_type: Type of engagement (like, reply, retweet, view)
        """
        stat_key = f"author_{author_id}"

        if stat_key not in self.stats:
            self.stats[stat_key] = ExplorationStats()

        if was_engaged:
            self.stats[stat_key].successes += 1
        else:
            self.stats[stat_key].failures += 1

        # Record in history
        self.exploration_history.append({
            "tweet_id": tweet_id,
            "author_id": author_id,
            "engaged": was_engaged,
            "engagement_type": engagement_type,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _create_exploration_explanation(
        self,
        tweet: RankedTweet,
        is_exploration: bool,
    ) -> Dict:
        """
        Create explanation for why this item is in the feed.

        Args:
            tweet: The tweet being explained
            is_exploration: Whether this was selected for exploration

        Returns:
            Explanation dictionary
        """
        stat_key = f"author_{tweet.tweet.author_id}"
        stats_obj = self.stats.get(stat_key, ExplorationStats())

        explanation = {
            "tweet_id": tweet.tweet.tweet_id,
            "original_rank": tweet.rank,
            "selected_for": "exploration" if is_exploration else "exploitation",
            "reason": self._generate_exploration_reason(
                tweet, stats_obj, is_exploration
            ),
            "author_stats": {
                "successes": stats_obj.successes,
                "failures": stats_obj.failures,
                "engagement_rate": stats_obj.empirical_rate,
            },
        }

        return explanation

    def _generate_exploration_reason(
        self,
        tweet: RankedTweet,
        stats_obj: ExplorationStats,
        is_exploration: bool,
    ) -> str:
        """
        Generate human-readable reason for inclusion.

        Args:
            tweet: The tweet
            stats_obj: Engagement statistics
            is_exploration: Whether this was exploration

        Returns:
            Explanation string
        """
        if not is_exploration:
            return f"Highly relevant (score: {tweet.explanation.total_score:.2f})"

        # Exploration reasons
        if stats_obj.total_trials == 0:
            return "New author - exploring diverse voices"
        elif stats_obj.empirical_rate > 0.6:
            return f"Under-represented quality author (engagement rate: {stats_obj.empirical_rate:.1%})"
        elif self.strategy == ExplorationStrategy.THOMPSON_SAMPLING:
            return "High-potential content based on Bayesian sampling"
        elif self.strategy == ExplorationStrategy.UCB:
            return "High-uncertainty, high-potential content to discover new interests"
        else:
            return "Exploratory content to diversify your feed"

    def get_exploration_stats(self) -> Dict:
        """
        Get overall exploration statistics.

        Returns:
            Dictionary with exploration metrics
        """
        if not self.stats:
            return {
                "total_authors_tracked": 0,
                "average_engagement_rate": 0.0,
                "exploration_history_length": len(self.exploration_history),
            }

        engagement_rates = [
            stat.empirical_rate for stat in self.stats.values()
        ]

        return {
            "total_authors_tracked": len(self.stats),
            "average_engagement_rate": np.mean(engagement_rates),
            "engagement_rate_std": np.std(engagement_rates) if len(engagement_rates) > 1 else 0.0,
            "highest_engagement_author": max(
                self.stats.items(),
                key=lambda x: x[1].empirical_rate,
            )[0] if self.stats else None,
            "exploration_history_length": len(self.exploration_history),
            "strategy_used": self.strategy.value,
            "exploration_rate": self.exploration_rate,
        }

    def reset_stats(self) -> None:
        """Clear all exploration statistics"""
        self.stats.clear()
        self.exploration_history.clear()
