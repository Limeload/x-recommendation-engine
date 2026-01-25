"""
Synthetic User & Engagement Simulation Engine
Generates realistic synthetic personas and engagement patterns
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple
from .schemas import User, UserPersona, Tweet, EngagementEvent
from ..models.ranking_engine import RankingEngine


class SyntheticDataGenerator:
    """Generate synthetic users, tweets, and engagement patterns"""

    # Persona-specific interest templates
    PERSONA_INTERESTS = {
        UserPersona.FOUNDER: [
            "Startups",
            "AI",
            "ProductManagement",
            "Fundraising",
            "Technology",
            "Innovation",
        ],
        UserPersona.JOURNALIST: [
            "Technology",
            "AI",
            "Business",
            "Investigation",
            "Media",
            "Politics",
        ],
        UserPersona.ENGINEER: [
            "AI",
            "BackendDevelopment",
            "OpenSource",
            "DevOps",
            "MachineL",
            "Systems",
        ],
        UserPersona.INVESTOR: [
            "Startups",
            "Fintech",
            "AI",
            "Crypto",
            "Markets",
            "Investment",
        ],
        UserPersona.CONTENT_CREATOR: [
            "Technology",
            "SocialMedia",
            "Design",
            "Creativity",
            "Community",
            "Marketing",
        ],
        UserPersona.RESEARCHER: [
            "AI",
            "MachineLearning",
            "DataScience",
            "Academia",
            "Papers",
            "Theory",
        ],
        UserPersona.ANALYST: [
            "Technology",
            "Business",
            "Analytics",
            "Markets",
            "Data",
            "Trends",
        ],
    }

    PERSONA_EXPERTISE = {
        UserPersona.FOUNDER: ["ProductManagement", "StartupGrowth", "Leadership"],
        UserPersona.JOURNALIST: ["Investigation", "WritingTechnique", "Interviewing"],
        UserPersona.ENGINEER: ["SystemsDesign", "CodeArchitecture", "Performance"],
        UserPersona.INVESTOR: ["ValuationModels", "RiskAssessment", "DealStructure"],
        UserPersona.CONTENT_CREATOR: ["ContentStrategy", "VideoProduction", "Engagement"],
        UserPersona.RESEARCHER: ["ResearchMethodology", "StatisticalAnalysis", "PeerReview"],
        UserPersona.ANALYST: ["DataAnalysis", "MarketResearch", "Forecasting"],
    }

    TOPICS_POOL = [
        "AI",
        "LLMs",
        "Startups",
        "Crypto",
        "Finance",
        "Technology",
        "Design",
        "DataScience",
        "OpenSource",
        "Web3",
        "CloudComputing",
        "Blockchain",
        "Robotics",
        "Quantum",
        "Biology",
    ]

    TWEET_TEMPLATES = {
        UserPersona.FOUNDER: [
            "Just shipped a new feature for {topics}! Excited about the response.",
            "Raising series A to solve {topics}. If interested, let's chat!",
            "How many startups are working on {topics}? Let me know in the replies.",
            "The future of {topics} is going to be crazy. Here's why...",
            "Learnings from our $X million round: {topics} is the next big thing",
        ],
        UserPersona.JOURNALIST: [
            "Breaking: Major announcement in {topics} today. Full investigation here.",
            "Why {topics} matters more than you think (explainer thread)",
            "Interview with CEO about the future of {topics}",
            "Inside look: How {topics} companies are disrupting the industry",
            "Did you miss this {topics} story? You won't believe what happened",
        ],
        UserPersona.ENGINEER: [
            "Just open-sourced our {topics} library. Check it out on GitHub!",
            "Deep dive into {topics} architecture. Here's what we learned...",
            "Performance tips for {topics} systems (1/5) 🧵",
            "Building scalable systems with {topics}. Code example below ↓",
            "RFC: New approach to {topics}. Thoughts?",
        ],
        UserPersona.INVESTOR: [
            "{topics} is the next $100B opportunity. Here's the thesis...",
            "We're investing in {topics}. Founders: apply here",
            "Q4 {topics} market analysis: Trends you need to know",
            "Why {topics} startups will win in 2026",
            "Track record: Invested in 5 {topics} companies in 2025",
        ],
    }

    @staticmethod
    def generate_user(
        user_id: str, username: str, persona: UserPersona
    ) -> User:
        """Generate a synthetic user with persona-specific interests"""
        return User(
            user_id=user_id,
            username=username,
            persona=persona,
            interests=random.sample(
                SyntheticDataGenerator.PERSONA_INTERESTS[persona], k=4
            ),
            expertise_areas=SyntheticDataGenerator.PERSONA_EXPERTISE[persona],
            follower_count=random.randint(100, 50000),
            bio=f"{persona.value.title()} passionate about technology and innovation",
        )

    @staticmethod
    def generate_tweet(
        tweet_id: str, author_id: str, persona: UserPersona
    ) -> Tweet:
        """Generate a synthetic tweet"""
        # Select 2-3 random topics
        topics = random.sample(SyntheticDataGenerator.TOPICS_POOL, k=random.randint(2, 3))
        topics_str = " + ".join(topics)

        # Get template
        templates = SyntheticDataGenerator.TWEET_TEMPLATES.get(
            persona,
            ["Thoughts on {topics}: what do you think?"],
        )
        content = random.choice(templates).format(topics=topics_str)

        # Add hashtags
        hashtags = [f"#{topic}" for topic in topics]

        # Generate realistic engagement metrics
        base_engagement = random.randint(10, 500)
        likes = int(base_engagement * random.uniform(1.0, 3.0))
        retweets = int(likes * random.uniform(0.1, 0.5))
        replies = int(likes * random.uniform(0.05, 0.2))
        bookmarks = int(likes * random.uniform(0.05, 0.15))

        # Quality score based on engagement and persona
        engagement_total = likes + retweets + replies + bookmarks
        quality_score = min(
            1.0,
            0.3 + (engagement_total / 5000.0)
            + random.uniform(-0.1, 0.1),  # Some noise
        )

        # Age: tweets created in the last 7 days
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 168))

        return Tweet(
            tweet_id=tweet_id,
            author_id=author_id,
            content=content,
            created_at=created_at,
            likes=likes,
            retweets=retweets,
            replies=replies,
            bookmarks=bookmarks,
            topics=topics,
            hashtags=hashtags,
            quality_score=quality_score,
        )

    @staticmethod
    def generate_engagement_event(
        event_id: str,
        user_id: str,
        target_tweet_id: str,
        target_user_id: str,
    ) -> EngagementEvent:
        """Generate a synthetic engagement event"""
        event_types = ["like", "retweet", "reply", "bookmark"]
        event_type = random.choice(event_types)

        # Weights: likes are most common
        weights = [0.6, 0.2, 0.1, 0.1]
        event_type = random.choices(event_types, weights=weights)[0]

        return EngagementEvent(
            event_id=event_id,
            user_id=user_id,
            target_tweet_id=target_tweet_id,
            target_user_id=target_user_id,
            event_type=event_type,
            created_at=datetime.utcnow(),
            weight=1.0,
        )
