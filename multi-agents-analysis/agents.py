from crewai import Agent
from crewai_tools import (
    PGSearchTool,
)
from textwrap import dedent
from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI


# This is an example of how to define custom agents.
# You can define as many agents as you want.
# You can also define custom tasks in tasks.py
class CustomAgents:
    def __init__(self) -> None:
        self.db_search_tool = PGSearchTool(
            db_uri='sqlite:///laps.db', table_name='laps')
        # self.OpenAIGPT35 = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
        self.Ollama = Ollama(
            model="internlm2", base_url="http://localhost:11434", temperature=0.1)

    def data_analyst(self):
        return Agent(
            role="Senior Data Analyst specialist in tabular data analysis",
            backstory=dedent(f"""You excel in receiving large tabular data and 
                             extract all the relevant information, providing
                             always a complete and detailed report about the
                             data."""),
            goal=dedent(f"""Analyse a vector database containing car data for
                        a given session or race. This vector database contains
                        information about 2 drivers of the same team.

                        You should analyse each driver separately, then
                        compare each other to highlight key differences
                        between them."""),
            allow_delegation=False,
            verbose=True,
            llm=self.Ollama,
            tools=[self.db_search_tool]
        )

    def race_engineer(self):
        return Agent()
