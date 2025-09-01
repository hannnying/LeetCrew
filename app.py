import os
from agentic.crew import LeetCrewAI
# from db import driver
from logger import LeetCodeLogger
from utils import fetch_question_details, get_difficulty_stats, get_topic_performance_stats, get_unsolved_questions
import streamlit as st
from datetime import datetime
import json


def main():
    st.title("LeetCode Logger")
    user_id = st.text_input("User", value="user_001")

    question_slug = st.text_input("LeetCode Question Slug (e.g., two-sum)")
    db = LeetCodeLogger()
    print(f"neo4j DB: {db.driver}")

    if question_slug:
        question_data = fetch_question_details(question_slug.lower())
        if question_data:
            st.success(f"Found: {question_data['questionTitle']} ({question_data['difficulty']})")
            st.write("**Topics:**", map(lambda x: x["slug"], question_data["topicTags"]))
        else:
            st.error("Could not fetch question data. Check the slug.")

        st.subheader("Your Interaction")
        solved = st.checkbox("Solved?", value=False)
        time_spent = st.number_input("Time spent (minutes)", min_value=0.0, value=15.0)
        attempts = st.number_input("Number of attempts", min_value=1, value=1)
        hint_used = st.checkbox("Used hint?", value=False)
        watched_youtube = st.checkbox("Watched YouTube explanation?", value=False)
    
    if st.button("Log to Knowledge Graph"):
        interaction_data = {
            "solved": solved,
            "time_spent": time_spent,
            "attempts": attempts,
            "hint_used": hint_used,
            "watched_youtube": watched_youtube
        }

        db.log_interaction(
            user_id=user_id,
            question_data=question_data,
            interaction_data=interaction_data,
            timestamp_logged=datetime.now()
        )

    if st.button("Recommend a Question"):
        print(f"fetching user: {user_id} performance data by topic")
        user_performance_data = get_topic_performance_stats(user_id)
        performance_path = os.path.join(os.getcwd(), f"knowledge/{user_id}_topic_stats.json")
        
        with open(performance_path, "w") as f:
            json.dump(user_performance_data, f, indent=2)
            print(f"{user_id} performanced data stored in {f}.")

        print(f"fetching user: {user_id} performance data by difficulty")
        difficulty_performance_data = get_difficulty_stats(user_id)
        performance_path = os.path.join(os.getcwd(), f"knowledge/{user_id}_difficulty_stats.json")
        
        with open(performance_path, "w") as f:
            json.dump(difficulty_performance_data, f, indent=2)
            print(f"{user_id} difficulty performanced data stored in {f}.")
 

        print(f"fetching user: {user_id} unsolved questions")
        unsolved_questions = get_unsolved_questions(user_id)
        unsolved_path = os.path.join(os.getcwd(), f"knowledge/{user_id}_unsolved_questions.json")

        with open(unsolved_path, "w") as f:
            json.dump(unsolved_questions, f, indent=2)
            print(f"{user_id} unsolved questions data stored in {f}.")

        result = LeetCrewAI(user_id=user_id).crew().kickoff()

        if result:
            st.write("**Questions:**", result)
            for path in [performance_path, unsolved_path]:
                if os.path.exists(path):
                    os.remove(path)

if __name__=="__main__":
    main()