from db import driver

mock_interactions = mock_interactions = [
    {
        "user_id": "user_001",
        "question_id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "solved": True,
        "time_spent": 12.5,
        "attempts": 1,
        "hint_used": False,
        "watched_youtube": False,
        "date_logged": "2025-08-21T15:30:00Z",
        "topics": ["Array", "Hash Table"],
        "similar_questions": ["3sum", "four-sum", "subarray-sum-equals-k"]
    },
    {
        "user_id": "user_001",
        "question_id": "reverse-linked-list",
        "title": "Reverse Linked List",
        "difficulty": "Medium",
        "solved": False,
        "time_spent": 40.0,
        "attempts": 3,
        "hint_used": True,
        "watched_youtube": True,
        "date_logged": "2025-08-19T10:00:00Z",
        "topics": ["Linked List", "Recursion"],
        "similar_questions": ["swap-nodes-in-pairs", "linked-list-cycle"]
    },
    {
        "user_id": "user_001",
        "question_id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "solved": True,
        "time_spent": 8.0,
        "attempts": 1,
        "hint_used": False,
        "watched_youtube": False,
        "date_logged": "2025-08-20T14:00:00Z",
        "topics": ["Stack", "String"],
        "similar_questions": ["min-remove-to-make-valid-parentheses", "generate-parentheses"]
    },
    {
        "user_id": "user_001",
        "question_id": "merge-intervals",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "solved": True,
        "time_spent": 25.0,
        "attempts": 2,
        "hint_used": False,
        "watched_youtube": True,
        "date_logged": "2025-08-18T09:30:00Z",
        "topics": ["Array", "Sorting"],
        "similar_questions": ["insert-interval", "interval-list-intersections"]
    },
    {
        "user_id": "user_001",
        "question_id": "3sum",
        "title": "3sum",
        "difficulty": "Medium",
        "solved": False,
        "time_spent": 30.0,
        "attempts": 1,
        "hint_used": True,
        "watched_youtube": True,
        "date_logged": "2025-08-18T09:30:00Z",
        "topics": ["Array", "Two-Pointers"],
        "similar_questions": ["two-sum", "4sum", "3sum-closest"]
    },
    {
        "user_id": "user_001",
        "question_id": "regular-expression-matching",
        "title": "Regular Expression Matching",
        "difficulty": "Hard",
        "solved": False,
        "time_spent": 45.0,
        "attempts": 2,
        "hint_used": True,
        "watched_youtube": True,
        "date_logged": "2025-08-18T09:30:00Z",
        "topics": ["String", "Dynamic Programming", "Recursion"],
        "similar_questions": ["wildcard-matching", "edit-distance"]
    }
]


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

WITH q, $similar_questions AS similar_questions
UNWIND similar_questions AS similar_question_id
    MERGE (similar_q:Question {question_id: similar_question_id})
    MERGE (q)-[:SIMILAR_TO]->(similar_q)
"""

def load_mock_data(driver, interactions):
    print(driver)

    with driver.session(database="neo4j") as session:
        for interaction in interactions:
            session.run(query, **interaction)
    print(f"Loaded {len(interactions)} mock interactions.")

if __name__ == "__main__":
    load_mock_data(driver, mock_interactions)
    driver.close()
