"""
LLM-powered tweet generation using Claude (Anthropic) with template fallback.
Called at startup if ANTHROPIC_API_KEY is set; otherwise synthetic_data templates are used.
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Prompt templates per persona type
_PERSONA_PROMPTS = {
    "politician": (
        "You are a politician who tweets about policy, governance, and constituent issues. "
        "Write one authentic tweet (max 280 chars) about {topic}. "
        "Be direct, cite a specific action or stance, and sound like a real elected official. "
        "No hashtags. Return only the tweet text."
    ),
    "meme_account": (
        "You run a popular meme/humor account on social media. "
        "Write one witty, relatable tweet (max 280 chars) riffing on {topic}. "
        "Use internet humor, POV format, or absurdist observation. "
        "No hashtags unless they're part of the joke. Return only the tweet text."
    ),
    "trader": (
        "You are an experienced financial trader who tweets about markets and trading. "
        "Write one tweet (max 280 chars) with a specific market observation about {topic}. "
        "Include a concrete trade setup or risk management insight. "
        "End with 'Not financial advice.' Return only the tweet text."
    ),
    "founder": (
        "You are a startup founder who shares lessons building in public. "
        "Write one tweet (max 280 chars) with a specific insight about {topic}. "
        "Be concrete and specific — mention a real metric, decision, or failure. "
        "Return only the tweet text."
    ),
    "journalist": (
        "You are a tech journalist who breaks news and writes investigative pieces. "
        "Write one tweet (max 280 chars) reporting on or analyzing {topic}. "
        "Sound factual and newsy. Return only the tweet text."
    ),
    "engineer": (
        "You are a software engineer who shares technical insights. "
        "Write one tweet (max 280 chars) with a technical tip or observation about {topic}. "
        "Be precise and practical. Return only the tweet text."
    ),
    "investor": (
        "You are a venture capital investor who shares market thesis posts. "
        "Write one tweet (max 280 chars) with an investment insight about {topic}. "
        "Be specific about trends or portfolio observations. Return only the tweet text."
    ),
    "content_creator": (
        "You create educational content about technology and culture. "
        "Write one tweet (max 280 chars) about {topic} that would resonate with your audience. "
        "Be relatable and add value. Return only the tweet text."
    ),
    "researcher": (
        "You are an academic researcher posting about your work. "
        "Write one tweet (max 280 chars) sharing a research insight or paper result about {topic}. "
        "Be precise and cite a concrete finding. Return only the tweet text."
    ),
    "analyst": (
        "You are a market/tech analyst who shares data-driven takes. "
        "Write one tweet (max 280 chars) with a specific data point or analysis about {topic}. "
        "Be quantitative where possible. Return only the tweet text."
    ),
}


async def generate_llm_tweet(persona: str, topics: list[str]) -> Optional[str]:
    """
    Generate one tweet via the Anthropic Claude API.
    Returns None if no API key is available or generation fails.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)

        topic_str = ", ".join(topics[:2]) if topics else "technology"
        prompt_template = _PERSONA_PROMPTS.get(persona, _PERSONA_PROMPTS["founder"])
        prompt = prompt_template.format(topic=topic_str)

        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}],
        )
        content = message.content[0].text.strip()
        # Strip surrounding quotes if Claude added them
        content = content.strip('"').strip("'")
        return content[:280]
    except Exception as exc:
        logger.debug(f"LLM tweet generation failed for {persona}: {exc}")
        return None


async def generate_llm_tweets_for_users(users, db, count_per_user: int = 3) -> int:
    """
    Generate LLM tweets for all users and add them to the DB.
    Runs as a background task after startup.
    Returns the number of tweets generated.
    """
    from models.schemas import Tweet  # local import to avoid circular

    generated = 0
    tweet_counter_start = int(datetime.utcnow().timestamp())

    tasks = []
    for user in users:
        topics = user.interests[:3] if user.interests else ["Technology"]
        for i in range(count_per_user):
            tasks.append((user, topics, i))

    # Run generation concurrently in small batches
    for i in range(0, len(tasks), 5):
        batch = tasks[i : i + 5]
        results = await asyncio.gather(
            *[generate_llm_tweet(user.persona.value, topics) for user, topics, _ in batch],
            return_exceptions=True,
        )
        for (user, topics, idx), content in zip(batch, results):
            if isinstance(content, str) and content:
                tweet_id = f"llm_{tweet_counter_start}_{user.user_id}_{idx}"
                tweet = Tweet(
                    tweet_id=tweet_id,
                    author_id=user.user_id,
                    author_name=user.username,
                    content=content,
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 12)),
                    topics=topics,
                    hashtags=[f"#{t}" for t in topics],
                    likes=random.randint(5, 200),
                    retweets=random.randint(1, 50),
                    replies=random.randint(0, 20),
                    bookmarks=random.randint(0, 15),
                    quality_score=0.7 + random.uniform(-0.1, 0.2),
                )
                db.add_tweet(tweet)
                generated += 1
        await asyncio.sleep(0.2)  # rate-limit courtesy pause

    return generated
