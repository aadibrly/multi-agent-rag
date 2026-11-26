from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state import AgentState
from app.agents.rag_agent import rag_agent_node
from app.agents.sql_agent import sql_agent_node
from app.agents.router import router_node
from app.agents.synthesizer import synthesizer_agent_node

def router_query(state: AgentState) -> str:
    """Reads state['route'] set by the router node and returns the next node key."""
    selected_route = state.get("route", "rag")
    if selected_route == "sql":
        return "sql_agent"
    else:
        "rag_agent"

def build_workflow():

    workflow = StateGraph(AgentState)


    # registering nodes
    workflow.add_node("router", router_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("sql_agent", sql_agent_node)
    workflow.add_node("synthesizer", synthesizer_agent_node)

    #adding edges
    workflow.add_edge(START, "router")

    #conditional branch 
    workflow.add_conditional_edges(
        "router", router_query,
        {
            "sql_agent":"sql_agent",
            "rag_agent":"rag_agent"
        }
    )

    #directing both path to the synthesizer
    workflow.add_edge("sql_agent", "synthesizer")
    workflow.add_edge("rag_agent", "synthesizer")\

    #Exit Node
    workflow.add_edge("synthesizer", END)
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)

    return compiled_graph


agent_graph = build_workflow()
