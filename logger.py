import ast
from datetime import datetime
import db
from neo4j import GraphDatabase
from utils import fetch_question_details
import json


class LeetCodeLogger:
    def __init__(self):
        self.driver = db.driver

    
    def log_question(self, question_data: dict):
        """ 
        Input question_data (dict) from the endpoint and log the question into the database, 
        creating nodes and linking them to topics.
        """
        query = """
        MERGE (q:Question {question_id: $title_slug})
        SET q.difficulty = $difficulty

        WITH q
        UNWIND $topics AS topic
            MERGE (t:Topic {name: topic})
            MERGE (q)-[:HAS_TOPIC]->(t)

        RETURN q
        """

        if isinstance(question_data["topicTags"], list):
            topics = question_data["topicTags"]
        else:
            topics = ast.literal_eval(question_data["topicTags"])  # safely parse string → list

        # Ensure it's just slugs (strings), not dicts
        topics = [t["slug"] for t in topics]

        # Prepare parameters for the query
        parameters = {
            "title_slug": question_data["titleSlug"],
            "difficulty": question_data["difficulty"],
            "topics": topics
        }

        try:
            # Execute the query using your Neo4j driver
            result = self.driver.execute_query(query, parameters)
            print(f"Successfully loaded: {question_data["titleSlug"]}")
            return result[0]  # Optionally, return the result if you need to process the created Question node
        except Exception as e:
            # Handle any exceptions that might occur
            print(f"Error logging question: {e}")
            return None  # Or handle the error appropriately
    

    def log_similar_questions(self, question, similar_questions: list):
        """
        Log the similar questions for a given question.
        Creates relationships between the current question and its similar questions.
        """
        print(f"Main Question: {question}")
        print("\n")
        print("SIMILAR QUESTIONS")
        print(similar_questions)
        print(type(similar_questions))

        for similar_question in similar_questions:
            if isinstance(similar_question, dict):
                similar_question = similar_question
            else:
                similar_question = json.loads(similar_question)
            similar_title_slug = similar_question["titleSlug"]
            similar_question_data = fetch_question_details(similar_title_slug)
            self.log_question(similar_question_data)

            query = """
            MERGE (q:Question {question_id: $title_slug})
            MERGE (s:Question {question_id: $similar_title_slug})
            MERGE (q)-[:IS_SIMILAR_TO]->(s)
            MERGE (s)-[:IS_SIMILAR_TO]->(q)
            """

            parameters = {
            "title_slug": question["titleSlug"],
            "similar_title_slug": similar_title_slug
        }   
        
            self.driver.execute_query(query, parameters)

        return similar_questions


    def log_interaction(self, user_id, question_data, interaction_data, timestamp_logged):
        """
        Log a user's interaction with a question.
        Create question nodes and relationships between user and question, 
        and log interaction metadata such as time spent, attempts, and hints.
        """
        if timestamp_logged is None:
            timestamp_logged = datetime.now()

        # Ensure Question exists
        question_node = self.log_question(question_data)

        # Log the similar questions (if any)
        similar_questions = json.loads(question_data.get("similarQuestions", []))
        self.log_similar_questions(question_data, similar_questions)

        
        query = """MERGE (u:User {user_id: $user_id})
        MERGE (q:Question {question_id: $title_slug})
        MERGE (u)-[r:INTERACTED_WITH]->(q)
        SET r.solved = $solved,
            r.time_spent = $time_spent,
            r.attempts = $attempts,
            r.hint_used = $hint_used,
            r.watched_youtube = $watched_youtube,
            r.date_logged = datetime($timestamp_logged)
        """

        # form interaction relationship between user and question
        parameters = {
            "user_id": user_id,
            "title_slug": question_data["titleSlug"],
            "solved": interaction_data["solved"],
            "time_spent": interaction_data["time_spent"],
            "attempts": interaction_data["attempts"],
            "hint_used": interaction_data["hint_used"],
            "watched_youtube": interaction_data["watched_youtube"],
            "timestamp_logged": timestamp_logged
        }

        print(f"parameters for log interaction: {parameters}")

        self.driver.execute_query(query, parameters)
