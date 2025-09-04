import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from agentic.tools import rank_exploration_topics, rank_weak_topics, filter_unsolved_questions_by_topic
import os
import json
from agentic.models import Questions
import yaml


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


@CrewBase
class StrategySelectorCrew():
    def __init__(self, user_id):
        self.user_id = user_id

    @agent
    def strategy_selector(self) -> Agent:
        user_performance_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_topic_stats.json"]
        )  
        recently_solved_questions = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_recently_solved.json"]
        )
        return Agent(
            role="Strategy Selector",
            goal="""Given a user's problem-solving performance by topic and a record of recent questions solved,
      decide whether the user should focus on improving weak topics or explore less-practiced topics
      to broaden their skills.""",
            backstory="""You are an intelligent educational strategist embedded in a learning assistant system.
      Your responsibility is to analyze a user's strengths, weaknesses, and learning behavior,
      then recommend the most effective learning strategy: targeted practice on weak topics, or
      exploration of less familiar areas to promote skill growth.""",
            llm="openai/gpt-4o",
            verbose=True,
            knowledge_sources=[user_performance_data, recently_solved_questions]
        )


    @task
    def select_strategy_task(self) -> Task:
        return Task(
            description="""Analyze the user's performance metrics by topic and their recent activity to determine
      the best strategy for recommending questions.

      You are provided with two inputs:
      1. A dictionary where each key is a topic name (string), and each value is another dictionary containing:
        - count: number of questions attempted in this topic
        - accuracy: percentage of correct answers (0–100)
        - hints_usage: percentage of questions where hints were used (0–100)
        - youtube_watch_rate: percentage of questions where YouTube explanations were watched (0–100)

      2. A JSON list of the most recent 4 questions solved by the user.

      Use this information to decide whether the user should:
      - Focus on improving weak topics ("improve"), or
      - Explore less-attempted or unfamiliar topics ("exploration").""",
      expected_output="""Return a single string: either "improve" or "exploration".
      Do not include anything else.""",
      agent=self.strategy_selector()
        )
    
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.strategy_selector()],
            tasks=[self.select_strategy_task()],
            process=Process.sequential
        )


@CrewBase
class ImproveCrew():
    def __init__(self, user_id, past_user):
        self.user_id = user_id
        self.past_user = past_user


    @agent
    def performance_analyst(self) -> Agent:
        user_performance_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_topic_stats.json"]
        )
        return Agent(
            role="Performance Analyst",
            goal="""Analyze a user's problem-solving behavior on LeetCode and return a ranked list of topics the user is weakest in,
      as well as topics that require more exploration due to less exposure. Use raw interaction data,
      compute performance metrics, and prioritize topics based on how urgently improvement or exploration is needed.""",
            backstory="""You are a specialized performance analyst with deep knowledge of LeetCode-style problems and user interaction patterns.
      Your job is to identify learning gaps by analyzing the user's question-solving history,
      considering success rate, hint usage, reliance on YouTube explanations, and exposure to topics.
      Based on your analysis, you rank topics by their priority for improvement or exploration.""",
            llm="openai/gpt-4o",
            verbose=True,
            tools=[rank_weak_topics],
            knowledge_sources=[user_performance_data]
        )
    

    @task 
    def rank_topics_task(self) -> Task:
        return Task(
            description="""Given analyzed topic performance metrics, compute a combined weakness score for each topic
      based on accuracy, hint usage and YouTube watch rates. Return a ranked list of the top N
      topics ranked by combined weakness.""",
      expected_output="""A list of dictionaries, where each dictionary represents a weak topic and contains:
      - topic (string): the name of the topic
      - score (float): the combined weakness score (higher means the topic needs more improvement)
      [
        {
          "topic": "topic_name",
          "score": float               # Combined weakness score (higher means weaker)
        },
        ...
      ]""",
      agent=self.performance_analyst()
        )
    

    @agent
    def question_finder(self) -> Agent:
        # modify this to include csv file
        user_unsolved_questions = CSVKnowledgeSource(
            file_paths=[f"{self.user_id}_unsolved_questions.csv"]
        )
        return Agent(
            role="Unsolved Question Selector",
            goal="""Given a list of weak or underexplored topics and a CSV file of unsolved LeetCode questions,
      select questions that match at least one topic the user needs to work on.""",
            backstory="""You specialize in helping users improve by selecting the most appropriate practice questions they haven't solved yet.
            The questions are provided in a CSV file, with one-hot encoded topic columns such as "Array", "Graph", etc.
            Each row represents a question, and a value of 1 in a topic column means the question is tagged with that topic.
            Use the provided tool to filter questions based on the user's target topics.
            Your job is to recommend only those questions that are relevant to the user’s weak or unexplored areas.""",
            verbose=True,
            tools=[filter_unsolved_questions_by_topic],
            knowledge_sources=[user_unsolved_questions]
        )


    @task
    def select_questions_task(self) -> Task:
        return Task(
            description=""" 1. A list of topics where the user either struggles (weak topics) or has less exposure (less covered topics).
            2. A JSON knowledge base containing questions the user has not solved, along with their topics and difficulty.

            Your task is to select questions that are most relevant to these topics.
            Only choose questions that have at least one topic overlapping with the provided topics list.
            Return a list of matching question slugs with associated metadata.""",
            expected_output=""" A list of dictionaries, each containing the following fields:
            - question_id: the question identifier
            - difficulty: the difficulty level of the question
            - topics: a list of topics associated with the question
            Example:
            [
                {
                "slug": "two-sum",
                "topics": ["Array", "Hash Table"],
                "difficulty": "Easy"
                },
                ...
            ]""",
            agent=self.question_finder(),
            context=[self.rank_topics_task()]
        )
    
    
    @agent
    def scoring_agent(self) -> Agent:
        user_difficulty_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_difficulty_stats.json"]
        )
        user_performance_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_topic_stats.json"]
        )
        knowledge = [user_difficulty_data, user_performance_data]
        
        if self.past_user:
            past_recommendations_data = JSONKnowledgeSource(
                file_paths=[f"{self.user_id}_past_recommendations.json"]
            )
            knowledge.append(past_recommendations_data)

        return Agent(
            role="Scoring Agent for LeetCode Question Recommendations",
            goal="""Receive candidate unsolved questions, user's topic performance data, difficulty summary, 
            and history of past recommendations. Score and rank the questions based on alignment with 
            user's weak topics, appropriate difficulty level, and prior exposure. Recommend questions 
            that are most relevant for effective learning and engagement.""",
            backstory="""You are an intelligent scoring agent that balances multiple user signals to prioritize 
            questions for practice. You consider:
            
            - How weak the user is in each topic
            - The difficulty level they are most comfortable with (based on attempted/solved ratios)
            - How often and how recently a question was recommended

            Use the past recommendation history to improve variety and avoid fatigue:
            - If a question has been recommended **recently**, deprioritize it unless it is highly relevant.
            - If a question has been recommended **multiple times**, but never attempted, consider giving it a **final boost** (unless the user appears to ignore it).
            - Avoid recommending the same question too frequently.

            Your job is to rank questions in a way that balances **learning effectiveness**, **novelty**, and **repetition when necessary**.""",
            llm="openai/gpt-4o",
            verbose=True,
            knowledge_sources=knowledge
        )
    
    
    @task
    def scoring_task(self) -> Task:
        return Task(
            description=""" Score and rank candidate LeetCode questions for a user based on their topic weaknesses 
            and difficulty performance. The agent evaluates how well questions match the user's needs.

            - If the user can only solve medium questions, do not recommend any harder than medium.
            - Questions that match more weak topics are considered more important and should be ranked higher.""",
            expected_output="""A JSON list of recommended questions with fields: slug, topics, difficulty.
            Example:
            [
                {
                "slug": "two-sum",
                "topics": ["Array", "Hash Table"],
                "difficulty": "Easy"
                }
            ]""",
            agent=self.scoring_agent(),
            context=[self.select_questions_task()],
            output_json=Questions
        )
    

    @crew
    def crew(self) -> Crew:
        return Crew(
                    agents=[self.performance_analyst(), self.question_finder(), self.scoring_agent()],
                    tasks=[self.rank_topics_task(), self.select_questions_task(), self.scoring_task()],
                    process=Process.sequential,
                    memory=True
                )
    

@CrewBase
class ExploreCrew():
    def __init__(self, user_id):
        self.user_id = user_id


    @agent    
    def performance_analyst(self) -> Agent:
        user_performance_data = JSONKnowledgeSource(
            file_paths=[f"{self.user_id}_topic_stats.json"]
        )
        return Agent(
            role="Performance Analyst",
            goal="""Analyze a user's problem-solving behavior on LeetCode and return a ranked list of topics the user is weakest in,
      as well as topics that require more exploration due to less exposure. Use raw interaction data,
      compute performance metrics, and prioritize topics based on how urgently improvement or exploration is needed.""",
            backstory="""You are a specialized performance analyst with deep knowledge of LeetCode-style problems and user interaction patterns.
      Your job is to identify learning gaps by analyzing the user's question-solving history,
      considering success rate, hint usage, reliance on YouTube explanations, and exposure to topics.
      Based on your analysis, you rank topics by their priority for improvement or exploration.""",
            llm="openai/gpt-4o",
            verbose=True,
            tools=[rank_exploration_topics],
            knowledge_sources=[user_performance_data]
        )


    @task
    def rank_exploration_topics_task(self) -> Task:
        return Task(
            description="""Given analyzed topic performance metrics, compute a combined weakness score for each topic
      based on accuracy, hint usage and YouTube watch rates. Return a ranked list of the top N
      topics ranked by combined weakness.""",
      expected_output="""A list of dictionaries, where each dictionary represents a weak topic and contains:
      - topic (string): the name of the topic
      - score (float): the combined weakness score (higher means the topic needs more improvement)
      [
        {
          "topic": "topic_name",
          "score": float               # Combined weakness score (higher means weaker)
        },
        ...
      ]""",
      agent=self.performance_analyst()
        )
    

    

    @agent
    def question_finder(self) -> Agent:
        # modify this to include csv file
        user_unsolved_questions = CSVKnowledgeSource(
            file_paths=[f"{self.user_id}_unsolved_questions.csv"]
        )
        return Agent(
            role="Unsolved Question Selector",
            goal="""Given a list of weak or underexplored topics and a CSV file of unsolved LeetCode questions,
      select questions that match at least one topic the user needs to work on.""",
            backstory="""You specialize in helping users improve by selecting the most appropriate practice questions they haven't solved yet.
            The questions are provided in a CSV file, with one-hot encoded topic columns such as "Array", "Graph", etc.
            Each row represents a question, and a value of 1 in a topic column means the question is tagged with that topic.
            Use the provided tool to filter questions based on the user's target topics.
            Your job is to recommend only those questions that are relevant to the user’s weak or unexplored areas.""",
            llm="openai/gpt-4o",
            verbose=True,
            tools=[filter_unsolved_questions_by_topic],
            knowledge_sources=[user_unsolved_questions]
        )
    

    @task
    def select_exploration_questions_task(self) -> Task:
        return Task(
            description=""" 1. A list of topics where the user either struggles (weak topics) or has less exposure (less covered topics).
            2. A JSON knowledge base containing questions the user has not solved, along with their topics and difficulty.

            Your task is to select questions that are most relevant to these topics.
            Only choose questions that have at least one topic overlapping with the provided topics list.
            Return a list of matching question slugs with associated metadata.""",
            expected_output=""" A list of dictionaries, each containing the following fields:
            - question_id: the question identifier
            - difficulty: the difficulty level of the question
            - topics: a list of topics associated with the question
            Example:
            [
                {
                "slug": "two-sum",
                "topics": ["Array", "Hash Table"],
                "difficulty": "Easy"
                },
                ...
            ]""",
        agent=self.question_finder(),
        context=[self.rank_exploration_topics_task()]
        )
    

    @crew
    def crew(self) -> Crew:
        return Crew(
                    agents=[self.performance_analyst(), self.question_finder()],
                    tasks=[self.rank_exploration_topics_task(), self.select_exploration_questions_task()],
                    process=Process.sequential,
                    memory=True
                )
