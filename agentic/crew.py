import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from agentic.tools import get_question_recommendations, get_weak_topics
from typing import List

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

@CrewBase
class LeetCrewAI():
    """Leetcode Crew for analysis of performance on LeetCode questions and recommendations for prctice."""


    @agent
    def performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['performance_analyst'],
            verbose=True,
            tools=[get_weak_topics]
        )

    @agent
    def strategy_recommender(self) -> Agent:
        print(self.agents_config)
        return Agent(
            config=self.agents_config['strategy_recommender'],
            verbose=True,
            tools=[get_question_recommendations]
        )
    
    @task
    def analysis_task(self) -> Task:
        print(self.tasks_config)
        return Task(
            config=self.tasks_config['analysis_task']
        )
    
    @task
    def recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config["recommendation_task"]
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.performance_analyst(), self.strategy_recommender()],
            tasks=[self.analysis_task(), self.recommendation_task()],
            process=Process.sequential
        )