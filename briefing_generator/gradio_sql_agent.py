import os
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage
from rich.console import Console
from langchain_google_genai import ChatGoogleGenerativeAI

console = Console(style="chartreuse1 on grey7")

os.environ['LANGCHAIN_PROJECT'] = 'briefing-generator'

# Load environment variables
load_dotenv()

# Ensure required environment variables are set
if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY not found in environment variables.")

# Initialize database connection
db = SQLDatabase.from_uri("sqlite:///../db/Bahrain_2023_Q.db")

# Initialize LLM
# llm = ChatOpenAI(model="gpt-4-0125-preview")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Create SQL toolkit and tools
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

# Define system message
system = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.""".format(
    table_names=db.get_usable_table_names()
)

system_message = SystemMessage(content=system)

# Create agent
agent = create_react_agent(llm, tools, state_modifier=system_message)


def predict(message, _):
    response = agent.invoke({"messages": [HumanMessage(content=message)]})
    console.print("\nresponse:")
    console.print(response)

    for msg in reversed(response["messages"]):
        if isinstance(msg, AIMessage):
            console.print("\nmsg:")
            console.print(msg)
            return msg.content


gr.ChatInterface(predict, type="messages").launch()
