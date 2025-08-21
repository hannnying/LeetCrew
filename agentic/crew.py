from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools import get_question_recommendations, get_weak_topics

@CrewBase
class LeetCrewAI():
    def __init__(self, agents_config: dict, tasks_config: dict):
        self.agents_config = agents_config
        self.tasks_config = tasks_config

    @agent
    def perforance_analyst(self) -> Agent:
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
            config=self.tasks_config["reearch_task"]
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.perforance_analyst(), self.strategy_recommender()],
            tasks=[self.analysis_task(), self.recommendation_task()],
            process=Process.sequential
        )