from datetime import date
from neo4j import GraphDatabase

class LeetCodeLogger:
    def __init__(self, driver):
        self.driver = driver
    
    def log_interaction(self, user_id, question_data, interaction_data, date_logged=date.today()):
        query = """
        MERGE (u:User {user_id: $user_id})
        MERGE (q:Question {question_id: $question_id})
        SET q.title = $title, q.difficulty = $difficulty

        MERGE (u)-[r:INTERACTED_WITH]->(q)
        SET r.solved = $solved,
            r.time_spent = $time_spent,
            r.attempts = $attempts,
            r.hint_used = $hint_used,
            r.watched_youtube = $watched_youtube,
            r.date_logged = datetime($date_logged)

        WITH q
        UNWIND $topics AS topic
            MERGE (t:Topic {name: topic})
            MERGE (q)-[:HAS_TOPIC]->(t)
        """

        parameters = {
            "user_id": user_id,
            "question_id": question_data["questionId"],
            "title": question_data["titleSlug"],
            "difficulty": question_data["difficulty"],
            "topics": question_data["topicTags"],
            "solved": interaction_data["solved"],
            "time_spent": interaction_data["time_spent"],
            "attempts": interaction_data["attempts"],
            "hint_used": interaction_data["hint_used"],
            "watched_youtube": interaction_data["watched_youtube"],
            "date_logged": date_logged
        }

        self.graph.run(query, parameters)