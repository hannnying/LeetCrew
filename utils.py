import requests
from db import driver


# LEETCODE_API = "https://alfa-leetcode-api.onrender.com" # replace with local host
LEETCODE_API = "http://localhost:3000" 

def fetch_question_details(question):
    """Fetch a LeetCode question and its metadata from the hosted API."""
    url = f"{LEETCODE_API}/select?titleSlug={question}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data 
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return None
    

def get_topic_performance_stats(user_id: str) -> dict:
    """
    Fetches raw interaction statistics for each topic attempted by the user.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        dict: A dictionary mapping each topic name to a nested dictionary containing:
            - count (int): Total number of questions attempted in this topic.
            - solved (int): Number of questions solved correctly.
            - hints_used (int): Number of times hints were used.
            - watched_youtube (int): Number of times user watched YouTube explanations.
    
    Example output:
    {
        "Dynamic Programming": {
            "count": 12,
            "solved": 6,
            "hints_used": 3,
            "watched_youtube": 1
        },
        ...
    }
    """
    query = """
    MATCH (u:User {user_id: $user_id})-[i:INTERACTED_WITH]->(q:Question)-[:HAS_TOPIC]->(t:Topic)
    RETURN 
      t.name AS topic,
      COUNT(q) AS count,
      SUM(CASE WHEN i.solved = true THEN 1 ELSE 0 END) AS solved,
      SUM(CASE WHEN i.hint_used = true THEN 1 ELSE 0 END) AS hints_used,
      SUM(CASE WHEN i.watched_youtube = true THEN 1 ELSE 0 END) AS watched_youtube
    ORDER BY count DESC
    """
    print(f"get topic performance stats user id: {user_id}")
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            topic_stats = {}
            for record in result:
                topic_name = record["topic"]
                topic_stats[topic_name] = {
                    "count": record["count"],
                    "solved": record["solved"],
                    "hints_used": record["hints_used"],
                    "watched_youtube": record["watched_youtube"]
                }
            return topic_stats
    finally:
        driver.close()