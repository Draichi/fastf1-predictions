import os
import gradio as gr
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from gradio import ChatMessage
import textwrap
from tools import (GetDriverPerformance, GetEventPerformance,
                   GetTelemetry, GetTyrePerformance, GetWeatherImpact)
from rich.console import Console
from db.connection import db

console = Console(style="chartreuse1 on grey7")

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
agent = create_react_agent(
    llm, tools, state_modifier=state_modifier)

# * Interact with agent


async def interact_with_agent(message, history):
    history.append(ChatMessage(role="user", content=message))
    yield history
    async for chunk in agent.astream({"messages": [HumanMessage(content=message)]}):

        if "tools" in chunk:
            messages = chunk["tools"]["messages"]
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    console.print(f"\n\n Used tool {msg.name}")
                    console.print(msg.content)
                    history.append(ChatMessage(
                        role="assistant", content=msg.content, metadata={"title": f"🛠️ Used tool {msg.name}"}))
                    yield history

        if "agent" in chunk:
            messages = chunk["agent"]["messages"]
            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.content:
                        console.print(f"\n\n💬 Assistant: {msg.content}")
                        console.print("-"*100)
                        history.append(ChatMessage(
                            role="assistant", content=msg.content, metadata={"title": "💬 Assistant"}))
                        yield history

# * Initialize Gradio
theme = gr.themes.Ocean()
with gr.Blocks(theme=theme, fill_height=True) as demo:
    gr.Markdown("""# Formula 1 Briefing Generator

                Welcome to the Formula 1 Briefing Generator - your AI-powered 
                assistant for comprehensive race analysis. 
                This innovative tool transforms complex Formula 1 race data into clear, 
                detailed reports automatically. 
                Whether you're interested in driver performance, tire strategies, or weather 
                impacts, our system analyzes telemetry data to provide insights that previously 
                required hours of expert analysis. This means teams, journalists, and fans 
                can now get instant, data-driven race breakdowns without needing technical expertise.

                To use this chatbot, simply type your question in the text box below. 
                You can ask about specific driver performances, compare lap times between teammates, 
                analyze tire degradation patterns, or understand how weather conditions affected the race. 
                Try starting with questions like _"How did Verstappen perform in the first sector?"_ or 
                _"Compare the tire strategies between Mercedes drivers."_ The AI will process your request 
                and provide detailed answers backed by real race data.""")
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
        "Highlight the telemetry data for Verstappen in the first lap",
        "Compare sector times between Hamilton and Russell",
        "Which driver had the best second sector?",
        "How did track temperature affect lap times throughout qualifying?"
    ], inputs=input)
    btn = gr.Button("Submit", variant="primary")
    btn.click(fn=interact_with_agent, inputs=[input, chatbot], outputs=chatbot)
    btn.click(lambda x: gr.update(value=''), [], [input])
    input.submit(lambda x: gr.update(value=''), [], [input])
    gr.Markdown(
        """---""")
    gr.Markdown("""## How We Process Formula 1 Data

    This application uses advanced AI techniques to translate your natural 
                language questions into precise database queries:

    1. **ReAct Agent**: The system uses a ReAct (Reasoning and Acting) agent that 
                breaks down complex questions into logical steps. For example, when you ask about tire strategies, the agent plans how to:
       - Query tire compound data
       - Analyze pit stop timing
       - Compare driver performances

    2. **RAG (Retrieval Augmented Generation)**: We enhance our responses by retrieving 
                relevant telemetry data from our Formula 1 database. This includes:
       - Lap times
       - Sector performances
       - Tire data
       - Weather conditions
       - Track temperatures

    3. **Text-to-SQL Translation**: Your natural language questions are converted into SQL 
                queries that extract precise data from our telemetry database. 
                The LLM understands racing context and generates accurate queries to fetch relevant information.

    This combination allows us to provide data-driven insights about any aspect of the race, 
                backed by real telemetry data.
                
    ## Next Steps

    We're continuously working to enhance this application's capabilities:

    1. **Expanded Race Coverage**:
       - Add telemetry data from more Grand Prix events
       - Include historical race data for trend analysis
       - Incorporate practice and qualifying session data

    2. **Vehicle Setup Database**:
       - Track car setup configurations for each team
       - Monitor setup changes between sessions
       - Analyze correlation between setup and performance

    3. **Simulator Integration**:
       - Connect with racing simulators for predictive modeling
       - Compare real telemetry with simulated data
       - Test strategy scenarios in virtual environments

    4. **Enhanced AI Capabilities**:
       - Fine-tune language models on racing-specific data
       - Add specialized tools for aerodynamic analysis
       - Implement predictive models for race strategy
       - Develop visual telemetry comparison tools

    5. **Advanced Analytics**:
       - Introduce machine learning for pattern recognition
       - Develop tire degradation prediction models
       - Add weather impact analysis tools
                
    Checkout the source code https://github.com/Draichi/formula1-AI don't forget to star the repo!""")


demo.launch()
