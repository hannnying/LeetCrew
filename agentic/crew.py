import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from agentic.tools import get_question_recommendations, get_weak_topics
import yaml

cwd = os.getcwd()

with open(os.path.join(cwd, r"agentic\config\agents_config.yaml"), "r") as f1:
    agents_config = yaml.safe_load(f1)

with open(os.path.join(cwd, r"agentic\config\tasks_config.yaml"), "r") as f2:
    tasks_config = yaml.safe_load(f2)
    print(tasks_config.keys())

@CrewBase
class LeetCrewAI():
    def __init__(self):
            
        with open(os.path.join(cwd, r"agentic\config\agents_config.yaml"), "r") as f1:
            agents_config = yaml.safe_load(f1)

        with open(os.path.join(cwd, r"agentic\config\tasks_config.yaml"), "r") as f2:
            tasks_config = yaml.safe_load(f2)
            print(tasks_config.keys())

        self.agents_config = agents_config
        self.tasks_config = tasks_config

    @agent
    def performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['performance_analyst'],
            verbose=True,
            tools=[get_weak_topics]
        )

    @agent
    def strategy_recommender(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_recommender'],
            verbose=True,
            tools=[get_question_recommendations]
        )
    
    @task
    def analysis_task(self) -> Task:
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