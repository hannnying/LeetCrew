import os
import requests
from db import driver
import datetime
import json
import pandas as pd


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
    

def get_all_topics(df):
    return list(df.columns[4:])


def get_topic_performance_stats(user_id: str, df: pd.DataFrame = pd.read_csv("data/questions.csv")) -> dict:
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
    topic_stats = {}
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
    finally:
        driver.close()
    
    all_topics = get_all_topics(df)
    for topic in all_topics:
        if topic not in topic_stats:
            topic_stats[topic] = {
                "count": 0,
                "solved": 0,
                "hints_used": 0,
                "watched_youtube": 0
            }
    return topic_stats


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
            "count": count,
            "accuracy": accuracy,
            "hints_usage": hints_usage,
            "youtube_watch_rate": youtube_watch_rate
        }

    return analyzed_performance


def get_recently_solved(user_id: str) -> dict:
    query = """
    MATCH (u:User {id: $user_id})-[i:INTERACTED_WITH]->(q:Question)-[:HAS_TOPIC]->(t:Topic)
    WHERE i.solved = true
    WITH q, i, collect(t.name) AS topics
    ORDER BY i.date_logged DESC
    LIMIT 4
    RETURN q.question_id AS id,
           q.difficulty AS difficulty,
           topics,
           i.date_logged AS date_logged
    """

    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            recently_solved = {}

            for record in result:
                question_id = record["question_id"]
                recently_solved[question_id] = {
                    "difficulty": record["difficulty"],
                    "topics": record["topics"],
                    "date_logged": record["date_logged"]
                }

            return recently_solved
        
    except Exception as e:
        print(f"Error retrieving recently solved questions: {e}")


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
    MATCH (u: User {user_id: $user_id})-[i:INTERACTED_WITH]->(q:Question)
    WHERE i.solved = true
    RETURN q.question_id AS question_id
    """
    all_questions = pd.read_csv("data\questions.csv")
    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            solved = list(map(lambda x: x["question_id"], result))
            unsolved = all_questions[~all_questions['title'].isin(solved)]
            return unsolved
    finally:
        driver.close()
            

def serialize_datetime(obj):
    """Serialize datetime objects"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def save_knowledge(user_id: str, data: dict, filename: str, filetype: str):
    os.makedirs("knowledge", exist_ok=True)
    path = os.path.join(os.getcwd(), f"knowledge/{user_id}_{filename}.{filetype.lower()}")

    if filetype.lower() == "json":
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✓] JSON data saved to: {path}")
        return path

    elif filetype.lower() == "csv":
        if isinstance(data, pd.DataFrame):
            data.to_csv(path, index=False)
            print(f"[✓] CSV data saved to: {path}")
            return path
        else:
            raise ValueError("To save as CSV, 'data' must be a pandas DataFrame.")
    else:
        raise ValueError("filetype must be 'json' or 'csv'")
