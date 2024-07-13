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
from decouple import config

from textwrap import dedent
from agents import CustomAgents
from tasks import CustomTasks

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search

from langchain.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
os.environ["OPENAI_ORGANIZATION"] = config("OPENAI_ORGANIZATION_ID")


class CustomCrew:
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def run(self):
        agents = CustomAgents()
