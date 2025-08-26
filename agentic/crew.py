import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from agentic.tools import analyse_topic_performance, rank_weak_topics
import os
from typing import List
import json

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

@CrewBase
class LeetCrewAI():
    """Leetcode Crew for analysis of performance on LeetCode questions and recommendations for prctice."""

    def __init__(self, user_id):
        self.user_id = user_id

    @agent
    def performance_analyst(self) -> Agent:
        user_performance_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_topic_stats.json"]
        )    
        return Agent(
            config=self.agents_config['performance_analyst'],
            verbose=True,
            tools=[analyse_topic_performance, rank_weak_topics],
            knowledge_sources=[user_performance_data]
        )


    @task
    def analyze_topic_performance_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_topic_performance_task']
        )


    @task
    def rank_weak_topics_task(self) -> Task:
        return Task(
            config=self.tasks_config['rank_weak_topics_task'],
            context=[self.analyze_topic_performance_task()]
        )
        

    @agent
    def question_finder(self) -> Agent:
        user_unsolved_questions = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_unsolved_questions.json"]
        )
        return Agent(
            config=self.agents_config["question_finder"],
            verbose=True,
            knowledge_sources=[user_unsolved_questions]
        )


    @task
    def select_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config["select_questions_task"],
            context=[self.rank_weak_topics_task()]
        )
    
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.performance_analyst(), self.question_finder()],
            tasks=[self.analyze_topic_performance_task(), self.rank_weak_topics_task(), self.select_questions_task()],
            process=Process.sequential
        )