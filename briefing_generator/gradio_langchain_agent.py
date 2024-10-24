import os
from click import progressbar
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage
from rich.console import Console
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import ast
from gradio import ChatMessage
import re

console = Console(style="chartreuse1 on grey7")

os.environ['LANGCHAIN_PROJECT'] = 'gradio-test'

# Load environment variables
load_dotenv()

# # Ensure required environment variables are set
# if not os.environ.get("OPENAI_API_KEY"):
#     raise EnvironmentError(
#         "OPENAI_API_KEY not found in environment variables.")

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


def query_as_list(db, query):
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))


drivers = query_as_list(db, "SELECT driver_name FROM Drivers")

# todo: Use here the queries Views saved in the db as a retriever named "search_telemetry_data"

vector_db = FAISS.from_texts(drivers, OpenAIEmbeddings())
retriever = vector_db.as_retriever(search_kwargs={"k": 5})
description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
valid proper nouns. Use the noun most similar to the search."""

retriever_tool = create_retriever_tool(
    retriever,
    name="search_proper_nouns",
    description=description,
)
tools.append(retriever_tool)

# Define system message
system = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

You have access to the following tables: {table_names}

If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool!
Do not try to guess at the proper name - use this function to find similar ones.""".format(
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


async def interact_with_agent(message, history):
    history.append(ChatMessage(role="user", content=message))
    yield history
    async for chunk in agent.astream({"messages": [HumanMessage(content=message)]}):

        if "tools" in chunk:
            messages = chunk["tools"]["messages"]
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    history.append(ChatMessage(
                        role="assistant", content=msg.content, metadata={"title": f"🛠️ Used tool {msg.name}"}))
                    yield history

        console.print(f"\nchunk:")
        console.print(chunk)
        if "agent" in chunk:
            messages = chunk["agent"]["messages"]
            console.print(f"\nmessages:")
            console.print(messages)
            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.content:
                        history.append(ChatMessage(
                            role="assistant", content=msg.content, metadata={"title": "💬 Assistant"}))
                        yield history

theme = gr.themes.Ocean(
    # primary_hue="sky",
    # secondary_hue="pink",
)

with gr.Blocks(theme=theme, fill_height=True) as demo:
    gr.Markdown("# Formula 1 Briefing Generator")
    chatbot = gr.Chatbot(
        type="messages",
        label="Agent interaction",
        avatar_images=(
            "https://upload.wikimedia.org/wikipedia/en/c/c6/NeoTheMatrix.jpg",
            "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
        ),
        scale=1,
        placeholder="Ask me any question about the 2023 Bahrain Grand Prix",
        layout="panel"
    )
    input = gr.Textbox(
        lines=1, label="Ask me any question about the 2023 Bahrain Grand Prix")
    input.submit(interact_with_agent, [
        input, chatbot], [chatbot])
    examples = gr.Examples(examples=[
        "How many fastest laps did Verstappen achieve?",
        "How many pit stops did Hamilton make?"
    ], inputs=input)
    btn = gr.Button("Submit", variant="primary")
    btn.click(fn=interact_with_agent, inputs=[input, chatbot], outputs=chatbot)
    btn.click(lambda x: gr.update(value=''), [], [input])
    input.submit(lambda x: gr.update(value=''), [], [input])


demo.launch()


# gr.ChatInterface(interact_with_agent,
#                  type="messages",
#                  chatbot=gr.Chatbot(type="messages",
#                                     value=[{"role": "user", "content": "What is the weather in San Francisco?"},
#                                            {"role": "assistant", "content": "I need to use the weather API tool",
#                                             "metadata": {"title":  "🧠 Thinking"}}]
#                                     ),
#                  #  textbox=gr.Textbox(
#                  #      placeholder="Ask me any question about the 2023 Bahrain Grand Prix", container=False, scale=7),
#                  title="foo bar",
#                  theme="soft",
#                  ).launch(debug=True)
