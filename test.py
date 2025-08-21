from db import driver

mock_interactions = [
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
        "notes": "Solved on first try",
        "date_logged": "2025-08-21T15:30:00Z",
        "topics": ["Array", "Hash Table"]
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
        "notes": "Had trouble with pointers",
        "date_logged": "2025-08-19T10:00:00Z",
        "topics": ["Linked List", "Recursion"]
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
        "notes": "Simple stack problem",
        "date_logged": "2025-08-20T14:00:00Z",
        "topics": ["Stack", "String"]
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
        "notes": "Used sorting technique",
        "date_logged": "2025-08-18T09:30:00Z",
        "topics": ["Array", "Sorting"]
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
    r.notes = $notes,
    r.date_logged = datetime($date_logged)

WITH q
UNWIND $topics AS topic
    MERGE (t:Topic {name: topic})
    MERGE (q)-[:HAS_TOPIC]->(t)
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
