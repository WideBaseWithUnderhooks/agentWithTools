from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from src.tools import TOOLS
import json

# 1. Define the Graph State
class AgentState(TypedDict):
    # 'add_messages' appends to history rather than overwriting
    messages: Annotated[list, add_messages]

# 2. Initialize Model and Bind Tools
llm = ChatOllama(model="llama3.2:3b", temperature=0).bind_tools(TOOLS)

# 3. Define the Node logic
def call_model(state: AgentState):
    """The decision-making node."""
    response = llm.invoke(state["messages"])
    
    # If model generated JSON but didn't parse it into tool_calls, parse it manually
    if not response.tool_calls and isinstance(response.content, str):
        try:
            tool_obj = json.loads(response.content)
            if isinstance(tool_obj, dict) and "name" in tool_obj:
                # Map human-readable tool names to actual function names
                tool_name_map = {
                    "Search the web": "web_search",
                }
                actual_name = tool_name_map.get(tool_obj["name"], tool_obj["name"])
                
                from langchain_core.messages import ToolCall
                tool_call = ToolCall(
                    name=actual_name,  # Use mapped name
                    args=tool_obj.get("parameters", {}),
                    id="1",
                )
                response.tool_calls = [tool_call]
        except (json.JSONDecodeError, KeyError):
            pass
    
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(TOOLS))

workflow.add_edge(START, "agent")

# Use prebuilt conditional logic to decide if we call tools or finish
workflow.add_conditional_edges("agent", tools_condition)

# Always return to the agent after tool execution to synthesize results
workflow.add_edge("tools", "agent")

app = workflow.compile()