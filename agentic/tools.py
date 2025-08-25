from crewai.tools import tool
from db import driver


@tool
def analyse_topic_performance(performance_stats: dict) -> dict:
    """
    Transforms raw topic statistics into normalized performance metrics and flags improvement needs.

    Args:
        performance_stats (dict): A dictionary with raw stats per topic as returned by
            `get_topic_performance_stats`. Expected keys for each topic include:
            - count (int)
            - solved (int)
            - hints_used (int)
            - watched_youtube (int)

    Returns:
        dict: A dictionary mapping each topic name to a nested dictionary with:
            - accuracy (float): Percentage of questions solved correctly.
            - hints_usage (float): Percentage of questions where hints were used.
            - youtube_watch_rate (float): Percentage of questions where YouTube explanations were watched.
    
    Notes:
        - Percentages are rounded to two decimal places.
        - Handles division by zero when count is zero.
    
    Example output:
    {
        "Dynamic Programming": {
            "accuracy": 50.0,
            "hints_usage": 25.0,
            "youtube_watch_rate": 8.33
        },
        ...
    }
    """
    analyzed_performance = {}

    for topic, stats in performance_stats.items():
        count = stats.get("count", 0)

        if count == 0:
            # Avoid division by zero by setting all percentages to 0
            accuracy = 0.0
            hints_usage = 0.0
            youtube_watch_rate = 0.0
        else:
            accuracy = round(stats.get("solved", 0) / count * 100, 2)
            hints_usage = round(stats.get("hints_used", 0) / count * 100, 2)
            youtube_watch_rate = round(stats.get("watched_youtube", 0) / count * 100, 2)

        analyzed_performance[topic] = {
            "accuracy": accuracy,
            "hints_usage": hints_usage,
            "youtube_watch_rate": youtube_watch_rate
        }

    return analyzed_performance


@tool
def rank_weak_topics(performance_analysis: dict, 
                     weights: dict = None,
                     top_k: int = 3) -> list:
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



@tool("Recommend LeetCode questions based on user's weak topics")
def get_question_recommendations(user_id: str, topics: list) -> list:
    """
    Given a user_id and a list of weak topics, return up to 3 recommended problems
    for that user in these topics.
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    UNWIND $topics AS topic_name
    MATCH (q:Question)-[:HAS_TOPIC]->(t:Topic {name: topic_name})
    RETURN q.title AS title, t.name AS topic, q.difficulty AS difficulty
    ORDER BY q.difficulty ASC  // easier questions first
    LIMIT 3
    """

    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id, topics=topics)
            recommendations = []
            for record in result:
                recommendations.append(record["title"])
            return recommendations
    finally:
        driver.close()