"""
Main file of the crewAI agents project for race analysis, role-playing as a race engineer.

This script serves as the entry point for the crewAI agents project, which focuses on 
analyzing race data and providing strategic insights. 

To run this file, ensure that you have installed the required 
dependencies specified in the requirements.yml file within your Conda virtual environment.

Setup Instructions:
1. Create and activate a Conda virtual environment.
2. Install the dependencies using the following command:
   conda env create --file requirements.yml
3. Paste your OpenAI key in the .env file.
4. Run this script to start the race analysis.

Usage:
   python main.py
"""

import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from textwrap import dedent
from agents import CustomAgents
from tasks import CustomTasks

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search

from langchain.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()


class CustomCrew:
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def run(self):
        agents = CustomAgents()
        tasks = CustomTasks()

        data_analyst_agent = agents.data_analyst()
        custom_agent_2 = agents.race_engineer()

        custom_task_1 = tasks.task_1_name(data_analyst_agent, 'foo', 'var')
        custom_task_2 = tasks.task_2_name(custom_agent_2)

        crew = Crew(agents=[data_analyst_agent, custom_agent_2], tasks=[
                    custom_task_1, custom_task_2], verbose=True)

        result = crew.kickoff()

        return result


if __name__ == "__main__":
    print("## Welcome to Crew AI Template")
    print("-------------------------------")
    var1 = input(dedent("""Enter variable 1: """))
    var2 = input(dedent("""Enter variable 2: """))

    custom_crew = CustomCrew(var1, var2)
    result = custom_crew.run()
    print("\n\n########################")
    print("## Here is you custom crew run result:")
    print("########################\n")
    print(result)
