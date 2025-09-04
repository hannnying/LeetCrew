import os
from agentic.crew import StrategySelectorCrew, ImproveCrew, ExploreCrew
from db import driver
from logger import LeetCodeLogger
from utils import (
    analyse_topic_performance,
    fetch_question_details,
    get_difficulty_stats,
    get_recently_solved, 
    get_topic_performance_stats,
    get_unsolved_questions,
    save_knowledge,
    serialize_datetime
)
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
        user_performance_data = analyse_topic_performance(
            get_topic_performance_stats(user_id)
        )
        performance_path = save_knowledge(user_id, user_performance_data, "topic_stats", "json")

        print(f"fetching recently solved questions by {user_id}")
        recently_solved = get_recently_solved(user_id)
        recently_solved_path = save_knowledge(user_id, recently_solved, "recently_solved", "json")

        strategy_result = StrategySelectorCrew(user_id=user_id).crew().kickoff()

        print(f"fetching user: {user_id} performance data by difficulty")
        difficulty_performance_data = get_difficulty_stats(user_id)
        difficulty_path = save_knowledge(user_id, difficulty_performance_data, "difficulty_stats", "json")

        print(f"fetching user: {user_id} unsolved questions")
        unsolved_questions = get_unsolved_questions(user_id)
        unsolved_path = save_knowledge(user_id, unsolved_questions, "unsolved_questions", "csv")


        memory_path = os.path.join(os.getcwd(), f"knowledge/{user_id}_past_recommendations.json")
        # check if memory exists, if not initialise it with an empty dict
        if not os.path.exists(memory_path):
            past_user = False
            past_recommendations = {}
        else:
            with open(memory_path, "r") as f:
                try:
                    past_recommendations = json.load(f)
                except json.JSONDecodeError:
                    past_recommendations = {}
            past_user = True
        

        if str(strategy_result) == "improve":
            result = ImproveCrew(user_id=user_id, past_user=past_user).crew().kickoff()
        
        elif str(strategy_result) == "exploration":
            result = ExploreCrew(user_id=user_id).crew().kickoff()    

        if result:
            st.write("**Questions:**", result)
            for path in [performance_path, recently_solved_path, difficulty_path, unsolved_path]:
                if os.path.exists(path):
                    os.remove(path)

            for q in result["questions"]:
                print(f"now what is q: {q}, {type(q)}, {len(q)}")
                question_id = q["slug"]
                if question_id not in past_recommendations:
                    past_recommendations[question_id] = {
                        "timestamp": json.dumps(datetime.now(), default=serialize_datetime),
                        "count": 1
                    }
                else:
                    past_recommendations[question_id]["timestamp"] = json.dumps(datetime.now(), default=serialize_datetime)
                    past_recommendations[question_id]["count"] += 1
            
            with open(memory_path, "w") as f:
                json.dump(past_recommendations, f, indent=2)
                print(f"updated memory on {datetime.now()}")
                

if __name__=="__main__":
    main()