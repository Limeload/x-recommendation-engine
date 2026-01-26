"""
Spam Detection and Content Moderation
Classifies content for spam, abuse, and quality issues
"""

from typing import Dict, List, Tuple
from enum import Enum


class ContentSafetyLevel(str, Enum):
    """Content safety classification"""
    SAFE = "safe"
    WARNING = "warning"
    HARMFUL = "harmful"
    SPAM = "spam"


class SpamDetector:
    """
    Spam and content safety detector.
    Uses heuristic rules and basic pattern matching.
    For production: use ML models (e.g., XGBoost, neural networks)
    """

    # Spam indicators
    SPAM_KEYWORDS = {
        "click here", "buy now", "limited offer", "act now", "subscribe",
        "follow back", "like for like", "check dm", "dm for details",
        "crypto", "nft", "free money", "make $", "earn cash", "work from home"
    }

    # Abusive/harmful keywords
    HARMFUL_KEYWORDS = {
        "hate", "kill", "attack", "destroy", "violent", "threat",
        "racist", "sexist", "homophobic", "transphobic"
    }

    def __init__(self):
        self.spam_threshold = 0.5
        self.harmful_threshold = 0.3

    def detect_spam_signals(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect spam signals in content.
        Returns: (spam_score: 0-1, reasons: List[str])
        """
        text_lower = text.lower()
        reasons = []
        spam_score = 0.0

        # Check for spam keywords
        keyword_matches = sum(1 for keyword in self.SPAM_KEYWORDS if keyword in text_lower)
        if keyword_matches > 0:
            spam_score += min(keyword_matches * 0.2, 0.4)
            reasons.append(f"Contains {keyword_matches} spam keyword(s)")

        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.5:
            spam_score += 0.2
            reasons.append("Excessive capitalization")

        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if c in "!?$*") / len(text) if text else 0
        if punct_ratio > 0.15:
            spam_score += 0.15
            reasons.append("Excessive punctuation")

        # Check for links (suspicious if multiple)
        link_count = text.count("http://") + text.count("https://")
        if link_count > 2:
            spam_score += 0.25
            reasons.append(f"Contains {link_count} links")

        # Check for repetition
        words = text.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:
                spam_score += 0.15
                reasons.append("Repetitive content")

        return min(spam_score, 1.0), reasons

    def detect_harmful_content(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect harmful/abusive content.
        Returns: (harm_score: 0-1, reasons: List[str])
        """
        text_lower = text.lower()
        reasons = []
        harm_score = 0.0

        # Check for harmful keywords
        keyword_matches = sum(1 for keyword in self.HARMFUL_KEYWORDS if keyword in text_lower)
        if keyword_matches > 0:
            harm_score += min(keyword_matches * 0.4, 0.8)
            reasons.append(f"Contains {keyword_matches} harmful keyword(s)")

        # Check for targeted harassment indicators
        if any(word in text_lower for word in ["you're", "you are", "you all"]):
            # Higher risk if combined with harmful keywords
            if keyword_matches > 0:
                harm_score += 0.2
                reasons.append("Targeted language detected")

        return min(harm_score, 1.0), reasons

    def classify_content(self, text: str, quality_score: float = 0.5) -> Dict:
        """
        Classify content for safety and quality.

        Args:
            text: Tweet content
            quality_score: Quality score from ranking (0-1)

        Returns:
            Dictionary with classification results
        """
        spam_score, spam_reasons = self.detect_spam_signals(text)
        harm_score, harm_reasons = self.detect_harmful_content(text)

        # Determine safety level
        if harm_score >= self.harmful_threshold:
            safety_level = ContentSafetyLevel.HARMFUL
        elif spam_score >= self.spam_threshold:
            safety_level = ContentSafetyLevel.SPAM
        elif spam_score > 0.3 or harm_score > 0.15:
            safety_level = ContentSafetyLevel.WARNING
        else:
            safety_level = ContentSafetyLevel.SAFE

        # Combined risk score
        risk_score = (spam_score * 0.6 + harm_score * 0.4)

        # Adjust based on quality
        adjusted_risk = max(0, risk_score - quality_score * 0.2)

        return {
            "safety_level": safety_level,
            "risk_score": risk_score,
            "adjusted_risk_score": adjusted_risk,
            "spam_score": spam_score,
            "harm_score": harm_score,
            "reasons": spam_reasons + harm_reasons,
            "recommendation": self._get_recommendation(safety_level, risk_score)
        }

    def _get_recommendation(self, safety_level: ContentSafetyLevel, risk_score: float) -> str:
        """Get action recommendation based on classification"""
        if safety_level == ContentSafetyLevel.HARMFUL:
            return "Block content - violates content policy"
        elif safety_level == ContentSafetyLevel.SPAM:
            return "Flag as spam - reduce ranking"
        elif safety_level == ContentSafetyLevel.WARNING:
            return "Demote ranking - may violate guidelines"
        else:
            return "Approve - content is safe"

    def calculate_moderation_multiplier(self, safety_level: ContentSafetyLevel) -> float:
        """
        Calculate ranking multiplier based on moderation assessment.
        Reduces ranking of questionable content.
        """
        multipliers = {
            ContentSafetyLevel.SAFE: 1.0,
            ContentSafetyLevel.WARNING: 0.5,
            ContentSafetyLevel.SPAM: 0.1,
            ContentSafetyLevel.HARMFUL: 0.0
        }
        return multipliers.get(safety_level, 1.0)


# Global spam detector
spam_detector = SpamDetector()


def init_spam_detector(detector: SpamDetector):
    """Initialize the global spam detector"""
    global spam_detector
    spam_detector = detector


def apply_content_moderation(tweet_score: float, safety_level: ContentSafetyLevel) -> float:
    """
    Apply content moderation to ranking score.

    Args:
        tweet_score: Original ranking score (0-100)
        safety_level: Content safety classification

    Returns:
        Moderated score
    """
    multiplier = spam_detector.calculate_moderation_multiplier(safety_level)
    return tweet_score * multiplier
