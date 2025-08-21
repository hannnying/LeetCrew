from crewai.tools import tool


@tool("Get weak topics for a user based on their struggles in the past week")
def get_weak_topics(driver, user_id: str) -> str:
    """
    Analyzes Neo4j graph data and returns the top 3 weak topics for a given user ID
    based on hint usage, YouTube views, or failure to solve.
    """
    query = """
    MATCH (u:User {id: $user_id})-[r:INTERACTED_WITH]->(q:Problem)-[:HAS_TOPIC]->(t:Topic)
    WHERE r.date_logged >= datetime() - duration({days: 7})
      AND (r.watched_youtube OR r.hint_used OR r.solved = false)
    RETURN t.name AS topic, count(*) AS weakness_signals
    ORDER BY weakness_signals DESC
    LIMIT 3
    """

    try:
        with driver.session() as session:
            result = session.run(query, user_id=user_id)
            topics = [record["topic"] for record in result]
            return {"user_id": user_id, "weak_topics": topics}

    finally:
        driver.close()


@tool("Recommend LeetCode questions based on user's weak topics")
def get_question_recommendations(driver, user_id: str, topics: list) -> list:
    """
    Given a user_id and a list of weak topics, return up to 3 recommended problems
    for that user in these topics.
    """
    query = """
    MATCH (u:User {id: $user_id})
    UNWIND $topics AS topic_name
    MATCH (q:Problem)-[:HAS_TOPIC]->(t:Topic {name: topic_name})
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