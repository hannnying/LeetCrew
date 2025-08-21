import os
from agentic.crew import LeetCrewAI
from db import driver
from dotenv import load_dotenv
from logger import LeetCodeLogger
from utils import fetch_question_details
import streamlit as st

def main():
    st.title("LeetCode Logger")
    user_id = st.text_input("User", value="han-ying")

    question_slug = st.text_input("LeetCode Question Slug (e.g., two-sum)")
    db = LeetCodeLogger(driver)

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
            user_id,
            question_data,
            interaction_data
        )

    if st.button("Recommend a Question"):
        result = LeetCrewAI().crew().kickoff(inputs={"user_id": user_id})

        if result:
            st.write("**Questions:**", result)

if __name__=="__main__":
    main()