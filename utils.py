import requests
from db import driver
import datetime


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


def fetch_all_questions(limit):
    """Fetch LeetCode questions and its metadata from the hosted API."""
    url = f"{LEETCODE_API}/problems?limit={limit}"
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


def get_difficulty_stats(user_id: str) -> dict:
    query = """
    MATCH (u:User {id: $user_id})-[i:INTERACTED_WITH]->(q:Question)
    WITH q.difficulty AS difficulty,
        COUNT(i) AS attempted,
        SUM(CASE WHEN i.solved = true THEN 1 ELSE 0 END) AS solved
    RETURN difficulty, attempted, solved
    """

    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            difficulty_stats = {}
            for record in result:
                level = record["difficulty"]
                difficulty_stats[level] = {
                    "count": record["attempted"],
                    "solved": record["sovlved"]
                }
            return difficulty_stats
    finally:
        driver.close()



def get_unsolved_questions(user_id: str) -> dict:
    query = """
    MATCH (q:Question)-[:HAS_TOPIC]->(t:Topic)
    WHERE NOT EXISTS {
    MATCH (:User {user_id: $user_id})-[i:INTERACTED_WITH]->(q)
    WHERE i.solved = true
    }
    RETURN q.question_id AS question_id, q.difficulty AS difficulty, collect(t.name) AS topics
    """
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            unsolved_questions = {}
            for record in result:
                question = record["question_id"]
                unsolved_questions[question] = {
                    "difficulty": record["difficulty"],
                    "topics": record["topics"]
                }
            return unsolved_questions
    finally:
        driver.close()


def serialize_datetime(obj):
    """Serialize datetime objects"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
