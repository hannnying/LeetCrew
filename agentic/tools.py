from agentic.models import DataFrameWrapper, Question, Questions
from crewai.tools import tool
import pandas as pd
from typing import List



@tool
def rank_weak_topics(performance_analysis: dict, 
                     weights: dict = None,
                     top_k: int = 5) -> list:
    """
    Rank topics by combined weakness score based on accuracy, hints usage, and youtube watch rate.

    Args:
        performance_analysis (dict): Output from `analyse_topic_performance`.
        weights (dict): Weights for each metric, keys: "accuracy", "hints_usage", "youtube_watch_rate".
            Defaults to {'accuracy': 0.5, 'hints_usage': 0.2, 'youtube_watch_rate': 0.2}.
        top_k (int): Number of top weak topics to return.

    Returns:
        list: List of top_k topics ordered from weakest to less weak, with their scores.
        Example: [{"topic": "Graphs", "score": 0.78}, ...]
    """

    if weights is None:
        weights = {'accuracy': 0.5, 'hints_usage': 0.2, 'youtube_watch_rate': 0.2}

    scored_topics = []

    for topic, metrics in performance_analysis.items():
        # Normalize accuracy to 0..1 where 1 = worst (lowest accuracy)
        acc_score = 1 - (metrics.get("accuracy", 0) / 100)
        hints_score = metrics.get("hints_usage", 0) / 100
        yt_score = metrics.get("youtube_watch_rate", 0) / 100

        combined_score = (
            weights['accuracy'] * acc_score +
            weights['hints_usage'] * hints_score +
            weights['youtube_watch_rate'] * yt_score
        )

        scored_topics.append({"topic": topic, "score": combined_score})

    # Sort descending by score (highest weakness first)
    scored_topics.sort(key=lambda x: x["score"], reverse=True)

    return scored_topics[:top_k]


@tool
def rank_exploration_topics(performance_analysis: dict, top_k: int = 5) -> list:
    """
    Ranks topics that are less explored by the user (e.g. fewer attempts).

    Args:
        performance_analysis (dict): Output from `analyse_topic_performance`. 
            Each topic has `count`, `accuracy`, `hints_usage`, `youtube_watch_rate`.
        top_k (int): Number of least explored topics to return.

    Returns:
        list: List of top_k least explored topics with their counts.
        Example: [{"topic": "Graphs", "count": 2}, ...]
    """
    if not performance_analysis:
        return []

    topic_counts = [
        {"topic": topic, "count": metrics.get("count", 0)}
        for topic, metrics in performance_analysis.items()
    ]

    # Sort ascending by attempt count (least explored first)
    topic_counts.sort(key=lambda x: x["count"])

    return topic_counts[:top_k]


@tool
def filter_unsolved_questions_by_topic(df: DataFrameWrapper, topics: List[str]) -> Questions:
    """
    Filters questions by topics (1-hot encoded) and returns only title, topics, difficulty.
    """
    # Validate topic columns exist
    missing = [t for t in topics if t not in df.columns]
    if missing:
        raise ValueError(f"Topic columns not found in DataFrame: {missing}")

    # Filter rows where any of the topic columns is 1
    mask = df[topics].any(axis=1)
    filtered_df = df[mask]

    # Keep only needed columns (ensure they exist)
    for col in ["title", "topics", "difficulty"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    filtered_df = filtered_df[["title", "topics", "difficulty"]].rename(columns={'title': 'slug'})
    return [Question(**row) for row in filtered_df.to_dict(orient="records")]