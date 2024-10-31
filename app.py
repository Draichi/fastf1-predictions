import os
import gradio as gr
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage
from rich.console import Console
from langchain_google_genai import ChatGoogleGenerativeAI
from gradio import ChatMessage
import textwrap
from tools import *
load_dotenv()
os.environ['LANGCHAIN_PROJECT'] = 'gradio-test'

# * Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# * Initialize tools
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

get_driver_performance_tool = GetDriverPerformance()
get_event_performance_tool = GetEventPerformance()
get_telemetry_tool = GetTelemetry()
get_tyre_performance_tool = GetTyrePerformance()
get_weather_impact_tool = GetWeatherImpact()

tools.append(get_driver_performance_tool)
tools.append(get_event_performance_tool)
tools.append(get_telemetry_tool)
tools.append(get_tyre_performance_tool)
tools.append(get_weather_impact_tool)

# * Initialize agent
agent_prompt = open("agent_prompt.txt", "r")
system_prompt = textwrap.dedent(agent_prompt.read())
agent_prompt.close()
state_modifier = SystemMessage(content=system_prompt)
agent = create_react_agent(llm, tools, state_modifier=state_modifier)

# * Interact with agent


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

# * Initialize Gradio
theme = gr.themes.Ocean()
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
