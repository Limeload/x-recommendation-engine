"""
FastAPI endpoints for LangChain-powered tweet generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from backend.simulation.langchain_tweet_generator import (
    PersonaTweetGenerator,
    GeneratedTweet,
    PersonaTemplate,
)

router = APIRouter(prefix="/api/generate", tags=["tweet-generation"])


class GenerateTweetsRequest(BaseModel):
    """Request to generate tweets"""
    persona_type: str  # "venture_capitalist", "engineer", "founder"
    count: int = 50
    export_format: Optional[str] = "json"  # json or csv


class GenerateTweetsResponse(BaseModel):
    """Response with generated tweets"""
    persona_name: str
    count: int
    tweets: List[GeneratedTweet]
    status: str = "success"


class PersonaListResponse(BaseModel):
    """Available personas"""
    personas: List[str]


# Initialize generator (would use dependency injection in production)
generator = None


def init_generator():
    """Initialize the LangChain generator"""
    global generator
    try:
        generator = PersonaTweetGenerator()
    except ValueError as e:
        print(f"Warning: LangChain generator not initialized: {e}")


@router.on_event("startup")
async def startup_event():
    """Initialize generator on startup"""
    init_generator()


@router.get("/personas", response_model=PersonaListResponse)
async def list_personas():
    """List available persona templates"""
    return PersonaListResponse(
        personas=[
            "venture_capitalist",
            "engineer",
            "founder",
        ]
    )


@router.post("/tweets", response_model=GenerateTweetsResponse)
async def generate_tweets(request: GenerateTweetsRequest):
    """
    Generate tweets using LangChain persona templates

    Args:
        request: GenerateTweetsRequest with persona_type and count

    Returns:
        GenerateTweetsResponse with generated tweets

    Example:
        ```
        POST /api/generate/tweets
        {
            "persona_type": "venture_capitalist",
            "count": 50
        }
        ```
    """
    if not generator:
        raise HTTPException(
            status_code=503,
            detail="LangChain generator not initialized. Check OpenAI API key.",
        )

    # Map persona types
    persona_map = {
        "venture_capitalist": generator.create_venture_capitalist_persona,
        "engineer": generator.create_engineer_persona,
        "founder": generator.create_founder_persona,
    }

    if request.persona_type not in persona_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona type: {request.persona_type}",
        )

    # Get persona
    persona = persona_map[request.persona_type]()

    # Validate count
    if request.count < 1 or request.count > 100:
        raise HTTPException(
            status_code=400,
            detail="Count must be between 1 and 100",
        )

    # Generate tweets (run in thread pool to avoid blocking)
    try:
        tweets = await asyncio.to_thread(
            generator.generate_tweets_batch,
            persona,
            request.count,
            False,  # No progress bar in API mode
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating tweets: {str(e)}",
        )

    return GenerateTweetsResponse(
        persona_name=persona.name,
        count=len(tweets),
        tweets=tweets,
        status="success",
    )


@router.post("/tweets/single")
async def generate_single_tweet(
    persona_type: str,
    style: Optional[str] = None,
):
    """
    Generate a single tweet

    Args:
        persona_type: Type of persona ("venture_capitalist", "engineer", "founder")
        style: Optional tweet style (uses random if not provided)

    Returns:
        GeneratedTweet
    """
    if not generator:
        raise HTTPException(
            status_code=503,
            detail="LangChain generator not initialized",
        )

    persona_map = {
        "venture_capitalist": generator.create_venture_capitalist_persona,
        "engineer": generator.create_engineer_persona,
        "founder": generator.create_founder_persona,
    }

    if persona_type not in persona_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona type: {persona_type}",
        )

    persona = persona_map[persona_type]()

    try:
        tweet = await asyncio.to_thread(
            generator.generate_tweet,
            persona,
            style,
        )
        return tweet
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating tweet: {str(e)}",
        )


@router.get("/personas/{persona_type}")
async def get_persona_details(persona_type: str):
    """
    Get details about a specific persona template

    Args:
        persona_type: Type of persona

    Returns:
        PersonaTemplate details
    """
    persona_map = {
        "venture_capitalist": lambda: PersonaTweetGenerator().create_venture_capitalist_persona(),
        "engineer": lambda: PersonaTweetGenerator().create_engineer_persona(),
        "founder": lambda: PersonaTweetGenerator().create_founder_persona(),
    }

    if persona_type not in persona_map:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown persona type: {persona_type}",
        )

    persona = persona_map[persona_type]()
    return persona.dict()
