from datetime import date
from neo4j import GraphDatabase
from utils import fetch_question_details

class LeetCodeLogger:
    def __init__(self, driver):
        self.driver = driver

    
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

        # Prepare parameters for the query
        parameters = {
            "title_slug": question_data["titleSlug"],
            "difficulty": question_data["difficulty"],
            "topics": question_data["topicTags"]
        }

        try:
            # Execute the query using your Neo4j driver
            result = self.driver.execute_query(query, parameters)
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
        for similar in similar_questions:
            similar_question_data = fetch_question_details(similar)
            self.log_question(similar_question_data)

            query = """
            MERGE (q:Question {question_id: $question_id})
            MERGE (s:Question {question_id: $similar_question_id})
            MERGE (q)-[:IS_SIMILAR_TO]->(s)
            MERGE (s)-[:IS_SIMILAR_TO]->(q)
            """

            parameters = {
            "question_id": question["question_id"],
            "similar_question_id": similar["titleSlug"]
        }   
        
            self.driver.execute_query(query, parameters)

        return similar_questions


    def log_interaction(self, user_id, question_data, interaction_data, date_logged=date.today()):
        """
        Log a user's interaction with a question.
        Create question nodes and relationships between user and question, 
        and log interaction metadata such as time spent, attempts, and hints.
        """

        # Ensure Question exists
        question_node = self.log_question(question_data)

        # Log the similar questions (if any)
        self.log_similar_questions(question_node, question_data.get("similar_questions", []))

        
        query = """MERGE (u:User {user_id $user_id})
        MERGE (q:Question {question_id: $question_id})
        MERGE (u)-[r:INTERACTED_WITH]->(q)
        SET r.solved = $solved,
            r.time_spent = $time_spent,
            r.attempts = $attempts,
            r.hint_used = $hint_used,
            r.watched_youtube = $watched_youtube,
            r.date_logged = datetime($date_logged)
        """

        # form interaction relationship between user and question
        parameters = {
            "user_id": user_id,
            "question_id": question_data["questionId"],
            "solved": interaction_data["solved"],
            "time_spent": interaction_data["time_spent"],
            "attempts": interaction_data["attempts"],
            "hint_used": interaction_data["hint_used"],
            "watched_youtube": interaction_data["watched_youtube"],
            "date_logged": date_logged
        }

        self.graph.run(query, parameters)

\