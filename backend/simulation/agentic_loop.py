"""
Agentic Loop: Autonomous agent personas that monitor the feed and make engagement decisions
based on their interest vectors. Agents can like or reply to tweets intelligently.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import random
import asyncio
from enum import Enum

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from pydantic import BaseModel

from backend.models.schemas import (
    User,
    Tweet,
    EngagementEvent,
    EngagementMetrics,
    RankingExplanation,
)
from backend.database.inmemory_db import InMemoryDB


class EngagementType(str, Enum):
    """Types of engagement an agent can make"""

    LIKE = "like"
    REPLY = "reply"
    BOOKMARK = "bookmark"
    RETWEET = "retweet"


class AgentDecision(BaseModel):
    """Decision made by an agent for a tweet"""

    tweet_id: str
    agent_id: str
    decision: EngagementType
    confidence: float  # 0-1, how confident the agent is
    reason: str  # Why the agent made this decision
    reply_content: Optional[str] = None  # If decision is REPLY


class InterestVector(BaseModel):
    """Vector representing agent's interests for scoring tweets"""

    interests: Dict[str, float]  # interest -> relevance weight (0-1)

    def compute_relevance(self, tweet_topics: List[str]) -> float:
        """
        Compute how relevant a tweet is based on interest vector

        Args:
            tweet_topics: Topics of the tweet

        Returns:
            Relevance score 0-1
        """
        if not tweet_topics:
            return 0.0

        if not self.interests:
            return 0.0

        # Calculate weighted relevance
        total_relevance = 0.0
        matched_topics = 0

        for topic in tweet_topics:
            # Check for exact match or similar keywords
            topic_lower = topic.lower()
            for interest, weight in self.interests.items():
                interest_lower = interest.lower()
                if topic_lower == interest_lower or interest_lower in topic_lower:
                    total_relevance += weight
                    matched_topics += 1

        # Normalize by number of topics
        if matched_topics > 0:
            return min(1.0, total_relevance / len(tweet_topics))

        return 0.0


class PersonaAgent:
    """
    Represents a persona as an autonomous agent that monitors feeds
    and makes engagement decisions
    """

    def __init__(
        self,
        user: User,
        db: InMemoryDB,
        api_key: Optional[str] = None,
        engagement_threshold: float = 0.6,
        reply_probability: float = 0.3,
    ):
        """
        Initialize a persona agent

        Args:
            user: User/persona that the agent represents
            db: Database for accessing tweets and storing engagement
            api_key: OpenAI API key for reply generation
            engagement_threshold: Min relevance score to engage (0-1)
            reply_probability: Probability of replying vs just liking (0-1)
        """
        self.user = user
        self.db = db
        self.engagement_threshold = engagement_threshold
        self.reply_probability = reply_probability

        # Create interest vector from user interests
        self.interest_vector = InterestVector(
            interests={interest: 1.0 for interest in user.interests}
        )

        # Initialize LLM for reply generation (optional)
        self.llm = None
        if api_key:
            self.llm = OpenAI(api_key=api_key, temperature=0.8, max_tokens=120)

        # Track engagement history
        self.engagement_history: List[AgentDecision] = []
        self.last_check_time = datetime.utcnow()

    def evaluate_tweet(self, tweet: Tweet) -> Tuple[bool, float, str]:
        """
        Evaluate if agent should engage with a tweet

        Args:
            tweet: Tweet to evaluate

        Returns:
            (should_engage, confidence, reason)
        """
        # Calculate relevance based on interest vector
        relevance = self.interest_vector.compute_relevance(tweet.topics)

        # Calculate recency bonus (recent tweets more likely to engage)
        age_hours = (datetime.utcnow() - tweet.created_at).total_seconds() / 3600
        recency_bonus = max(0, 1.0 - (age_hours / 24.0))  # Decay over 24 hours

        # Calculate engagement score (combination of relevance and quality)
        engagement_score = (
            0.6 * relevance
            + 0.2 * tweet.quality_score
            + 0.2 * min(1.0, recency_bonus)
        )

        should_engage = engagement_score >= self.engagement_threshold

        # Generate reason
        reasons = []
        if relevance > 0.7:
            reasons.append("highly relevant to interests")
        elif relevance > 0.5:
            reasons.append("moderately relevant")
        if tweet.quality_score > 0.8:
            reasons.append("high quality content")
        if recency_bonus > 0.8:
            reasons.append("recent post")

        reason = " + ".join(reasons) if reasons else "general interest"

        return should_engage, engagement_score, reason

    def decide_engagement_type(self) -> EngagementType:
        """
        Decide whether to like, reply, bookmark, or retweet

        Returns:
            Type of engagement to perform
        """
        rand = random.random()

        if rand < self.reply_probability:
            return EngagementType.REPLY
        elif rand < self.reply_probability + 0.3:
            return EngagementType.RETWEET
        elif rand < self.reply_probability + 0.5:
            return EngagementType.BOOKMARK
        else:
            return EngagementType.LIKE

    def generate_reply(self, tweet: Tweet) -> Optional[str]:
        """
        Generate a reply to a tweet using LangChain

        Args:
            tweet: Tweet to reply to

        Returns:
            Generated reply text or None if LLM not available
        """
        if not self.llm:
            return None

        template = """You are {persona_name}, a {description}.

A tweet was posted about {topic}:
"{tweet_content}"

Write a thoughtful, brief reply that:
1. Shows your expertise in {expertise}
2. Adds value to the conversation
3. Reflects your personality ({tone})
4. Is 280 characters or less

Reply:"""

        prompt = PromptTemplate(
            input_variables=[
                "persona_name",
                "description",
                "topic",
                "tweet_content",
                "expertise",
                "tone",
            ],
            template=template,
        )

        try:
            response = self.llm(
                prompt.format(
                    persona_name=self.user.name,
                    description=self.user.persona_type or "professional",
                    topic=", ".join(tweet.topics[:2]),
                    tweet_content=tweet.content[:100],
                    expertise=", ".join(self.user.expertise[:2]),
                    tone="professional" if "professional" in str(self.user) else "casual",
                )
            )
            return response.strip() if response else None
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    async def monitor_feed(
        self, tweets: List[Tweet], max_engagements_per_check: int = 5
    ) -> List[AgentDecision]:
        """
        Monitor feed and make engagement decisions

        Args:
            tweets: List of tweets to evaluate
            max_engagements_per_check: Max engagements per monitoring cycle

        Returns:
            List of decisions made
        """
        decisions = []
        engagements_made = 0

        # Shuffle tweets to get variety
        shuffled_tweets = random.sample(tweets, min(len(tweets), 20))

        for tweet in shuffled_tweets:
            if engagements_made >= max_engagements_per_check:
                break

            # Evaluate tweet
            should_engage, confidence, reason = self.evaluate_tweet(tweet)

            if should_engage:
                # Decide type of engagement
                engagement_type = self.decide_engagement_type()

                # Generate reply if needed
                reply_content = None
                if engagement_type == EngagementType.REPLY:
                    reply_content = self.generate_reply(tweet)

                # Create decision
                decision = AgentDecision(
                    tweet_id=tweet.id,
                    agent_id=self.user.id,
                    decision=engagement_type,
                    confidence=confidence,
                    reason=reason,
                    reply_content=reply_content,
                )

                decisions.append(decision)
                self.engagement_history.append(decision)
                engagements_made += 1

        self.last_check_time = datetime.utcnow()
        return decisions

    def apply_decisions(self, decisions: List[AgentDecision]) -> List[str]:
        """
        Apply engagement decisions to database

        Args:
            decisions: Decisions to apply

        Returns:
            List of engagement IDs created
        """
        engagement_ids = []

        for decision in decisions:
            try:
                # Update tweet engagement metrics
                tweet = self.db.tweets.get(decision.tweet_id)
                if not tweet:
                    continue

                # Update engagement metrics based on decision
                if decision.decision == EngagementType.LIKE:
                    tweet.engagement.likes += 1
                elif decision.decision == EngagementType.RETWEET:
                    tweet.engagement.retweets += 1
                elif decision.decision == EngagementType.BOOKMARK:
                    tweet.engagement.bookmarks += 1
                elif decision.decision == EngagementType.REPLY:
                    tweet.engagement.replies += 1

                    # Create reply tweet if content was generated
                    if decision.reply_content:
                        reply_tweet = Tweet(
                            id=f"reply_{self.user.id}_{decision.tweet_id}_{int(datetime.utcnow().timestamp())}",
                            author_id=self.user.id,
                            content=decision.reply_content,
                            topics=tweet.topics,  # Inherit topics
                            engagement=EngagementMetrics(),
                            quality_score=0.7,
                            created_at=datetime.utcnow(),
                        )
                        self.db.add_tweet(reply_tweet)

                # Create engagement event
                event = EngagementEvent(
                    user_id=self.user.id,
                    tweet_id=decision.tweet_id,
                    event_type=decision.decision.value,
                    timestamp=datetime.utcnow(),
                    reason=decision.reason,
                )

                self.db.add_engagement_event(event)
                engagement_ids.append(f"{self.user.id}_{decision.tweet_id}_{decision.decision.value}")

            except Exception as e:
                print(f"Error applying decision: {e}")

        return engagement_ids


class AgentManager:
    """Manages multiple persona agents and orchestrates agentic loop"""

    def __init__(self, db: InMemoryDB, api_key: Optional[str] = None):
        """
        Initialize agent manager

        Args:
            db: Database instance
            api_key: OpenAI API key for reply generation
        """
        self.db = db
        self.api_key = api_key
        self.agents: Dict[str, PersonaAgent] = {}
        self.check_interval = 300  # Check every 5 minutes
        self.is_running = False

    def create_agent(
        self,
        user: User,
        engagement_threshold: float = 0.6,
        reply_probability: float = 0.3,
    ) -> PersonaAgent:
        """
        Create and register a new agent

        Args:
            user: User/persona for the agent
            engagement_threshold: Min relevance to engage
            reply_probability: Probability of replying

        Returns:
            Created agent
        """
        agent = PersonaAgent(
            user=user,
            db=self.db,
            api_key=self.api_key,
            engagement_threshold=engagement_threshold,
            reply_probability=reply_probability,
        )
        self.agents[user.id] = agent
        return agent

    def get_agent(self, user_id: str) -> Optional[PersonaAgent]:
        """Get agent by user ID"""
        return self.agents.get(user_id)

    def get_all_agents(self) -> List[PersonaAgent]:
        """Get all registered agents"""
        return list(self.agents.values())

    async def agent_check_cycle(
        self, agent: PersonaAgent, max_engagements: int = 5
    ) -> List[AgentDecision]:
        """
        Run one monitoring cycle for an agent

        Args:
            agent: Agent to run cycle for
            max_engagements: Max engagements per cycle

        Returns:
            Decisions made
        """
        # Get recent tweets from feed
        all_tweets = list(self.db.tweets.values())
        recent_tweets = [t for t in all_tweets if t.author_id != agent.user.id]

        # Agent evaluates tweets
        decisions = await agent.monitor_feed(recent_tweets, max_engagements)

        # Apply decisions
        agent.apply_decisions(decisions)

        return decisions

    async def run_agentic_loop(self, num_cycles: int = 1):
        """
        Run the agentic loop for specified number of cycles

        Args:
            num_cycles: Number of monitoring cycles to run
        """
        self.is_running = True

        try:
            for cycle in range(num_cycles):
                print(f"\n🔄 Agentic Loop Cycle {cycle + 1}/{num_cycles}")
                print("=" * 60)

                # Run check for each agent concurrently
                tasks = [
                    self.agent_check_cycle(agent) for agent in self.agents.values()
                ]

                results = await asyncio.gather(*tasks)

                # Summary
                total_decisions = sum(len(r) for r in results)
                print(f"✅ Total engagements: {total_decisions}")

                for agent in self.agents.values():
                    if agent.engagement_history:
                        recent = agent.engagement_history[-5:]
                        engagements = [d.decision.value for d in recent]
                        print(f"   {agent.user.name}: {engagements}")

                if cycle < num_cycles - 1:
                    print(f"⏳ Next cycle in {self.check_interval} seconds...")
                    await asyncio.sleep(self.check_interval)

        finally:
            self.is_running = False

    def get_agent_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get statistics for an agent

        Args:
            user_id: User ID of agent

        Returns:
            Agent statistics
        """
        agent = self.get_agent(user_id)
        if not agent:
            return None

        history = agent.engagement_history
        engagement_counts = {
            "like": sum(1 for d in history if d.decision == EngagementType.LIKE),
            "reply": sum(1 for d in history if d.decision == EngagementType.REPLY),
            "retweet": sum(
                1 for d in history if d.decision == EngagementType.RETWEET
            ),
            "bookmark": sum(
                1 for d in history if d.decision == EngagementType.BOOKMARK
            ),
        }

        return {
            "user_id": user_id,
            "user_name": agent.user.name,
            "total_engagements": len(history),
            "engagement_counts": engagement_counts,
            "average_confidence": (
                sum(d.confidence for d in history) / len(history)
                if history
                else 0
            ),
            "last_check": agent.last_check_time.isoformat(),
            "interests": agent.user.interests,
        }

    def get_all_stats(self) -> List[Dict]:
        """Get statistics for all agents"""
        return [self.get_agent_stats(agent.user.id) for agent in self.agents.values()]

    def reset_agent_history(self, user_id: str) -> bool:
        """Reset engagement history for an agent"""
        agent = self.get_agent(user_id)
        if agent:
            agent.engagement_history = []
            return True
        return False
