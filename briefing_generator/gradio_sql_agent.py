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

console = Console(style="chartreuse1 on grey7")

# Load environment variables
load_dotenv()

# Ensure required environment variables are set
if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY not found in environment variables.")

# Initialize database connection
db = SQLDatabase.from_uri("sqlite:///../db/Bahrain_2023_Q.db")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-0125-preview")

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


class ChatbotState:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role, content):
        self.conversation_history.append((role, content))

    def get_conversation_history(self):
        return self.conversation_history

    def clear_history(self):
        self.conversation_history = []


chatbot_state = ChatbotState()


def process_message(user_input):
    chatbot_state.add_message("Human", user_input)

    response = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    console.print("\nresponse:")
    console.print(response)

    ai_message = next(
        (msg for msg in response["messages"] if isinstance(msg, AIMessage)), None)
    if ai_message:
        ai_response = ai_message.content
        console.print("\nai_response:")
        console.print(ai_response)
        chatbot_state.add_message("AI", ai_response)
        return ai_response
    else:
        error_message = "Sorry, I couldn't generate a response. Please try again."
        chatbot_state.add_message("AI", error_message)
        return error_message


def chat_interface(user_input):
    ai_response = process_message(user_input)
    return chatbot_state.get_conversation_history()


def clear_conversation():
    chatbot_state.clear_history()
    return chatbot_state.get_conversation_history()


def predict(message, history):
    history_langchain_format = []
    for msg in history:
        if msg['role'] == "user":
            history_langchain_format.append(
                HumanMessage(content=msg['content']))
        elif msg['role'] == "assistant":
            history_langchain_format.append(AIMessage(content=msg['content']))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm(history_langchain_format)
    console.print("\ngpt_response:")
    console.print(gpt_response)
    return gpt_response.content


# Create Gradio interface
iface = gr.ChatInterface(
    fn=predict,
    type="messages",
    title="F1 Database SQL Agent",
    description="Ask questions about the F1 Bahrain 2023 Qualifying database.",
    theme="default",
)

iface.launch()
