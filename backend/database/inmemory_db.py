"""
In-Memory Database for MVP
In production, replace with Pinecone/Weaviate for vector storage
and PostgreSQL/MongoDB for relational data
"""

from typing import List, Dict, Optional
from datetime import datetime
from models.schemas import Tweet, User, EngagementGraph, EngagementEvent


class InMemoryDB:
    """Simple in-memory database for prototyping"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.tweets: Dict[str, Tweet] = {}
        self.engagement_graphs: Dict[str, EngagementGraph] = {}
        self.tweet_embeddings: Dict[str, List[float]] = {}

    # User operations
    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user
        self.engagement_graphs[user.user_id] = EngagementGraph(user_id=user.user_id)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def update_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def get_all_users(self) -> List[User]:
        return list(self.users.values())

    # Tweet operations
    def add_tweet(self, tweet: Tweet) -> None:
        self.tweets[tweet.tweet_id] = tweet

    def get_tweet(self, tweet_id: str) -> Optional[Tweet]:
        return self.tweets.get(tweet_id)

    def get_all_tweets(self) -> List[Tweet]:
        return list(self.tweets.values())

    def get_user_tweets(self, user_id: str) -> List[Tweet]:
        return [t for t in self.tweets.values() if t.author_id == user_id]

    def search_tweets_by_topic(self, topic: str) -> List[Tweet]:
        return [t for t in self.tweets.values() if topic in t.topics]

    def search_tweets_by_keyword(self, keyword: str) -> List[Tweet]:
        keyword_lower = keyword.lower()
        return [
            t
            for t in self.tweets.values()
            if keyword_lower in t.content.lower()
            or any(keyword_lower in tag.lower() for tag in t.hashtags)
        ]

    def get_recent_tweets(self, limit: int = 50) -> List[Tweet]:
        sorted_tweets = sorted(self.tweets.values(), key=lambda t: t.created_at, reverse=True)
        return sorted_tweets[:limit]

    # Engagement operations
    def get_engagement_graph(self, user_id: str) -> EngagementGraph:
        if user_id not in self.engagement_graphs:
            self.engagement_graphs[user_id] = EngagementGraph(user_id=user_id)
        return self.engagement_graphs[user_id]

    def add_following(self, user_id: str, following_id: str) -> None:
        graph = self.get_engagement_graph(user_id)
        if following_id not in graph.following:
            graph.following.append(following_id)

        # Add reverse relationship
        follower_graph = self.get_engagement_graph(following_id)
        if user_id not in follower_graph.followers:
            follower_graph.followers.append(user_id)

    def add_engagement_event(self, user_id: str, event: EngagementEvent) -> None:
        graph = self.get_engagement_graph(user_id)
        graph.engagement_events.append(event)

        # Update engagement metrics on tweet
        if event.target_tweet_id in self.tweets:
            tweet = self.tweets[event.target_tweet_id]
            if event.event_type == "like":
                tweet.likes += 1
            elif event.event_type == "retweet":
                tweet.retweets += 1
            elif event.event_type == "reply":
                tweet.replies += 1
            elif event.event_type == "bookmark":
                tweet.bookmarks += 1

    def store_embedding(self, tweet_id: str, embedding: List[float]) -> None:
        self.tweet_embeddings[tweet_id] = embedding

    def get_embedding(self, tweet_id: str) -> Optional[List[float]]:
        return self.tweet_embeddings.get(tweet_id)

    def search_similar_tweets(
        self, tweet_embedding: List[float], top_k: int = 10
    ) -> List[Tweet]:
        """
        Simple cosine similarity search (placeholder for vector DB).
        In production, use Pinecone/Weaviate.
        """
        if not tweet_embedding:
            return []

        def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            mag1 = sum(a**2 for a in vec1) ** 0.5
            mag2 = sum(b**2 for b in vec2) ** 0.5
            return dot_product / (mag1 * mag2) if mag1 and mag2 else 0.0

        similarities = []
        for tweet_id, embedding in self.tweet_embeddings.items():
            sim = cosine_similarity(tweet_embedding, embedding)
            if tweet_id in self.tweets:
                similarities.append((self.tweets[tweet_id], sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in similarities[:top_k]]

    def get_trending_topics(self) -> Dict[str, int]:
        """Get trending topics across all tweets"""
        topic_counts: Dict[str, int] = {}
        for tweet in self.tweets.values():
            for topic in tweet.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))
