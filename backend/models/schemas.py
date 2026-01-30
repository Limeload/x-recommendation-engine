"""
Data Schemas for the Recommendation Engine
Defines: Users, Tweets, Engagement Graph, and Ranking Explanations
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class UserPersona(str, Enum):
    """Enumeration of user personas for synthetic simulation"""
    FOUNDER = "founder"
    JOURNALIST = "journalist"
    ENGINEER = "engineer"
    INVESTOR = "investor"
    CONTENT_CREATOR = "content_creator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"


class User(BaseModel):
    """User profile in the recommendation engine"""
    user_id: str
    username: str
    persona: UserPersona
    interests: List[str] = Field(default_factory=list)  # e.g., ["AI", "Blockchain", "Finance"]
    expertise_areas: List[str] = Field(default_factory=list)
    follower_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    bio: str = ""

    # Personalization profile
    preference_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "username": "alice_founder",
                "persona": "founder",
                "interests": ["AI", "StartupTechnology"],
                "expertise_areas": ["LLMs", "ProductManagement"],
                "follower_count": 5000,
                "bio": "Building the future of AI",
                "preference_weights": {
                    "recency": 0.2,
                    "popularity": 0.25,
                    "quality": 0.2,
                    "topic_relevance": 0.25,
                    "diversity": 0.1
                }
            }
        }


class Tweet(BaseModel):
    """Tweet document in the system"""
    tweet_id: str
    author_id: str
    author_name: Optional[str] = None  # Human-readable author name
    content: str
    created_at: datetime

    # Engagement metrics
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    bookmarks: int = 0

    # Content metadata
    topics: List[str] = Field(default_factory=list)  # e.g., ["AI", "LLMs"]
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)

    # Quality signals
    quality_score: float = 0.5  # 0-1 scale

    # Embeddings (stored as vectors in Pinecone/Weaviate)
    embedding_id: Optional[str] = None

    # Graph context
    in_reply_to_tweet_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    is_retweet: bool = False
    original_tweet_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tweet_id": "tweet_456",
                "author_id": "user_123",
                "content": "Just launched our AI-powered tool for founders...",
                "created_at": "2026-01-25T10:30:00Z",
                "likes": 150,
                "retweets": 45,
                "replies": 12,
                "bookmarks": 30,
                "topics": ["AI", "Startups"],
                "hashtags": ["#BuildInPublic", "#AI"],
                "mentions": ["@openai", "@anthropic"],
                "quality_score": 0.85,
                "embedding_id": "vec_123"
            }
        }


class EngagementEvent(BaseModel):
    """Engagement event in the social graph"""
    event_id: str
    user_id: str
    target_tweet_id: str
    target_user_id: str
    event_type: str  # "like", "retweet", "reply", "bookmark", "view"
    created_at: datetime
    weight: float = 1.0  # Importance weight for this engagement


class EngagementGraph(BaseModel):
    """User engagement graph"""
    user_id: str
    following: List[str] = Field(default_factory=list)
    followers: List[str] = Field(default_factory=list)
    engagement_events: List[EngagementEvent] = Field(default_factory=list)
    topic_affinities: Dict[str, float] = Field(default_factory=dict)  # Topic -> affinity score


class RankingExplanation(BaseModel):
    """Explanation metadata for why a tweet was ranked"""
    tweet_id: str
    total_score: float

    # Component scores with weights
    recency_score: float = Field(description="Score based on tweet freshness (0-1)")
    recency_weight: float

    popularity_score: float = Field(description="Score based on engagement metrics (0-1)")
    popularity_weight: float

    quality_score: float = Field(description="Content quality signal (0-1)")
    quality_weight: float

    topic_relevance_score: float = Field(description="Relevance to user interests (0-1)")
    topic_relevance_weight: float

    diversity_penalty: float = Field(description="Diversity/clustering penalty (0-1)")

    # Explanations
    key_factors: List[str] = Field(
        default_factory=list,
        description="Human-readable explanation factors"
    )

    persona_match: Optional[str] = Field(
        None,
        description="Which persona does this tweet match?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tweet_id": "tweet_456",
                "total_score": 0.82,
                "recency_score": 0.9,
                "recency_weight": 0.2,
                "popularity_score": 0.75,
                "popularity_weight": 0.25,
                "quality_score": 0.85,
                "quality_weight": 0.2,
                "topic_relevance_score": 0.88,
                "topic_relevance_weight": 0.25,
                "diversity_penalty": 0.05,
                "key_factors": [
                    "High affinity to 'AI' persona",
                    "Recent high-engagement content",
                    "Strong quality signals",
                    "Authored by followed user"
                ],
                "persona_match": "founder"
            }
        }


class RankedTweet(BaseModel):
    """A tweet with its ranking explanation"""
    tweet: Tweet
    explanation: RankingExplanation
    rank: int


class RankingRequest(BaseModel):
    """Request to rank tweets for a user"""
    user_id: str
    limit: int = Field(default=20, le=100)
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional filters (e.g., 'exclude_topics', 'min_quality')"
    )


class WeightTuningRequest(BaseModel):
    """Request to update ranking weights for a user"""
    user_id: str
    weights: Dict[str, float] = Field(
        description="Updated preference weights"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "weights": {
                    "recency": 0.1,
                    "popularity": 0.3,
                    "quality": 0.2,
                    "topic_relevance": 0.3,
                    "diversity": 0.1
                }
            }
        }
