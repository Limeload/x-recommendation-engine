/**
 * Type definitions for the recommendation engine
 */

export interface User {
  user_id: string;
  username: string;
  persona: string;
  interests: string[];
  expertise_areas: string[];
  follower_count: number;
  created_at: string;
  bio: string;
  preference_weights: Record<string, number>;
}

export interface Tweet {
  tweet_id: string;
  author_id: string;
  content: string;
  created_at: string;
  likes: number;
  retweets: number;
  replies: number;
  bookmarks: number;
  topics: string[];
  hashtags: string[];
  mentions: string[];
  quality_score: number;
  embedding_id?: string;
  in_reply_to_tweet_id?: string;
  in_reply_to_user_id?: string;
  is_retweet: boolean;
  original_tweet_id?: string;
}

export interface RankingExplanation {
  tweet_id: string;
  total_score: number;
  recency_score: number;
  recency_weight: number;
  popularity_score: number;
  popularity_weight: number;
  quality_score: number;
  quality_weight: number;
  topic_relevance_score: number;
  topic_relevance_weight: number;
  diversity_penalty: number;
  key_factors: string[];
  persona_match?: string;
}

export interface RankedTweet {
  tweet: Tweet;
  explanation: RankingExplanation;
  rank: number;
}

export interface EngagementEvent {
  event_id: string;
  user_id: string;
  target_tweet_id: string;
  target_user_id: string;
  event_type: string;
  created_at: string;
  weight: number;
}

export interface EngagementGraph {
  user_id: string;
  following: string[];
  followers: string[];
  engagement_events: EngagementEvent[];
  topic_affinities: Record<string, number>;
}
