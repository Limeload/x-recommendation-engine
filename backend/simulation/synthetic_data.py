"""
Synthetic User & Engagement Simulation Engine
Generates realistic synthetic personas and engagement patterns
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from models.schemas import User, UserPersona, Tweet, EngagementEvent
from models.ranking_engine import RankingEngine


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
            "Just shipped the new {topics} dashboard to 100k users yesterday. 47% increase in daily active usage. It's surreal seeing something you built for months suddenly clicked with people.\n\nEvery bug report feels like a gift right now because it means people actually care enough to complain.",
            "We're raising Series A. Not announcing terms yet but exploring {topics} partnerships.\n\nIf you're a founder in this space, let's grab coffee. Learning from 8 other teams right now - it's wild how many different angles work.",
            "Had this realization: everyone's complaining about {topics}, but nobody's fixing the root cause.\n\nSpent the last 3 months building something different. Beta launching next month with a completely different approach to the problem.",
            "The infrastructure gap in {topics} is getting ridiculous. AWS pricing alone kills 60% of startups trying to scale here.\n\nWe built our own solution. Open sourcing it next week. Sometimes the constraint forces the innovation.",
            "Failed product launch #3 yesterday. {topics} vertical just isn't ready.\n\nTurning attention to enterprise now. Revenue matters more than being first. Smart founders know this.",
            "Hot take: the entire {topics} industry is built backwards. Should be bottom-up, not top-down.\n\nWe're betting $2M on this thesis. Either brilliant or stupid in 18 months. No in-between.",
            "Onboarded our first 10k users for {topics} last week. Watching growth curves is addictive. The compounding effect is hitting different now.\n\nNext: build retention loops before scaling acquisition.",
        ],
        UserPersona.JOURNALIST: [
            "BREAKING: Major {topics} company just acquired competitor for undisclosed sum. 47 people laid off. Industry sources say deal valued at 8x revenue despite weakening market.\n\nFull investigation dropping tomorrow morning with internal emails.",
            "Spent 4 months investigating {topics} regulation. What I found is concerning.\n\nGovernments are 18 months behind the tech. Companies are exploiting grey zones. The reckoning comes in 2026.\n\nThread below.",
            "{topics} founder tells me they fabricated user numbers for Series B pitch. Not naming yet (legal review), but this is systemic.\n\nI've now found 3 separate cases. How many more exist?",
            "Interview series on {topics} drops this week. Talked to 12 founders, 8 investors, 3 regulators. The narrative everyone's sold isn't matching reality.\n\nMy instinct says market crashes before it soars.",
            "The {topics} story nobody covering: workers are getting exploited in ways the SEC doesn't track. Off-the-record conversations are wild.\n\nRaising freedom of information act requests next week.",
            "Everyone's talking about {topics} winners. I want to talk about the losers who taught us what doesn't work.\n\nSpending 6 months documenting failed experiments. Failure stories matter more than success stories.",
            "Podcast special this Friday: {topics} insiders predict what happens next. 90 minutes of unfiltered takes. Some statements might be controversial enough for Twitter drama (but that's the point).",
        ],
        UserPersona.ENGINEER: [
            "Open-sourced our {topics} infrastructure layer on GitHub. Handles 100k requests per second with single machine. MIT license.\n\nDocumentation is thorough. Community contributions welcome.",
            "Just spent 6 hours debugging a {topics} latency issue. Root cause was embarrassingly simple: one unindexed database column.\n\nThis is why I write detailed post-mortems. Learning for the team.",
            "Architecture thought: Most people solve {topics} with microservices. We consolidated to monolith and performance actually improved.\n\nLess operational overhead. Easier debugging. Counter-intuitive but the tradeoffs made sense for us.",
            "{topics} performance optimization is actually solved now. Here's what works:\n\n1. Cache aggressively\n2. Batch at boundaries\n3. Async where possible\n4. Monitor everything\n5. Iterate based on profiles not guesses\n\nWe went 1200ms to 80ms average latency.",
            "Built a {topics} system that horizontally scales without coordination overhead. No consensus algorithms needed.\n\nPaper incoming. Open-source implementation next month.",
            "My hot take: The {topics} stack everyone recommends is overengineered for 90% of use cases.\n\nStarter kit I released uses 70% fewer dependencies, simpler to understand, and faster in practice.",
            "Code review feedback on {topics} PR: We were doing distributed consensus wrong.\n\nFixed it. Now it's elegant. Sometimes simple is better than clever.",
        ],
        UserPersona.INVESTOR: [
            "{topics} market fundamentals shifted this quarter. TAM growing faster than expected. Just made 8 new investments based on updated models.\n\nExit potential: 5-8x returns minimum in 5 years for portfolio companies.",
            "Portfolio update: Our {topics} bets are outperforming sector.\n\n2.3x growth rate vs 1.8x median. This is why picking founders matters more than picking ideas.",
            "{topics} is entering hockey stick phase. Adoption curves remind me of mobile in 2010.\n\nExpect 100x return opportunities to emerge. Writing 50M check this month.",
            "Backed 5 {topics} companies in December. All raised within 30 days. Market velocity is insane.\n\nContrast to 18-month fundraising cycles from 2022. Founders are energized again.",
            "Interesting thesis: {topics} winners will be bottom-up, not top-down. Enterprise sales playbook is broken here.\n\nLooking for founders with 100k raving fans, not flashy Series A decks.",
            "{topics} funding climate is polarized. Winners raising at huge premiums. Zombies can't raise.\n\nNo middle ground. This feels healthy actually. Capital flowing to best ideas.",
            "Due diligence on {topics} target: Unit economics are there. Margin expansion is real. Scale is the only question.\n\nMoving forward with term sheet.",
        ],
        UserPersona.CONTENT_CREATOR: [
            "Published my {topics} explainer video (18 minutes). Simplified the technical jargon so anyone can understand.\n\n5k views in first hour. The algorithm is rewarding educational content again. Keep pushing.",
            "Making a {topics} course because the gap between 'beginner' and 'pro' content is massive.\n\nI'm positioned perfectly in the middle. Pre-launch list is 2k people already.",
            "{topics} community is starving for authentic perspectives. Not hype. Not jargon. Just real talk.\n\nThat's what I'm building. Let's grow something genuine together.",
            "Thread on why everyone's getting {topics} wrong:\n\n1. They optimize for hype\n2. They ignore fundamentals\n3. They follow leaders blind\n4. They don't test independently\n\nDo the opposite. That's how I positioned my channel.",
            "New {topics} podcast series launches next month. 10-part deep dive.\n\nInterviewed practitioners who've shipped real products. None of the theory-only stuff.",
            "Design breakdown: How {topics} UX improved 3x by removing one feature.\n\nSometimes less is more. Visual case study coming to my blog Thursday.",
            "{topics} trends I'm betting on for 2026:\n\n- Authenticity over polish\n- Niche over broad\n- Community over algorithm\n- Shipping over perfection\n\nBuilding my entire content strategy around this.",
        ],
        UserPersona.RESEARCHER: [
            "New research paper on {topics} just got accepted at top venue. 24-month project with 12 collaborators.\n\nFull PDF available. This changes some fundamental assumptions people hold.",
            "Benchmark dataset for {topics} released today: 500k examples, fully annotated, reproducible.\n\nAddress the reproducibility crisis in research. Science should be public.",
            "{topics} hypothesis confirmed through empirical testing. P-value < 0.001. Effect size is practically significant too.\n\nSubmitting to Nature next week.",
            "Literature review on {topics} reveals a troubling pattern: Most papers don't replicate.\n\nWe're doing a meta-analysis. Early results suggest experimental methodology needs revision.",
            "Statistical analysis on {topics} shows consensus is fragile. Small changes in assumptions create different conclusions.\n\nThis is important. Researchers need to think about robustness.",
            "{topics} benchmark leaderboard is live. Currently 47 teams competing. New SOTA model emerged from unexpected institution.\n\nThe best ideas don't always come from big labs.",
            "Peer review feedback suggests {topics} field has citation echo chambers. We're breaking that by pulling from 8 different subfields.\n\nInterdisciplinary work matters.",
        ],
        UserPersona.ANALYST: [
            "{topics} market report Q4 2025: $48B market, growing 32% YoY.\n\nSegmentation analysis:\n- Enterprise: $32B, slowing\n- Mid-market: $12B, accelerating\n- SMB: $4B, explosive growth\n\nWhere are you betting?",
            "Competitive landscape shift in {topics}:\n\nTier 1: 3 clear winners\nTier 2: 8 companies with viable paths\nTier 3: 20+ struggling for differentiation\n\nConsolidation wave coming within 18 months.",
            "{topics} pricing analysis shows winners charging 3x what losers charge for similar features.\n\nValue communication matters more than features. This is a sales problem, not a product problem.",
            "Adoption curves for {topics} across verticals:\n\n- Finance: 34% penetration (fastest)\n- Healthcare: 12% penetration (regulated)\n- Retail: 8% penetration (late stage)\n\nExpect healthcare to accelerate once compliance clears.",
            "{topics} customer acquisition cost is rising. Saturation is real in early adopter segments.\n\nWinners will win through retention and expansion. Net dollar retention is now the key metric.",
            "Funding landscape analysis: {topics} sector raised $3.2B in 2025, down from $4.1B in 2024.\n\nBut valuations held steady. Investors are being selective about quality.",
            "{topics} trend report: Moving from 'What is this?' to 'How do I use this?'\n\nContent strategy should reflect this maturity. Explainers are out, implementations are in.",
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
        tweet_id: str, author_id: str, persona: UserPersona, author_name: Optional[str] = None
    ) -> Tweet:
        """Generate a synthetic tweet"""
        # Select 2-3 random topics
        topics = random.sample(SyntheticDataGenerator.TOPICS_POOL, k=random.randint(2, 3))
        topics_str = topics[0]

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
            author_name=author_name,
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
