from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.core.state import AgentState

class RouteDecision(BaseModel):
    route: str= Field(
        description="One of: 'rag', 'sql', 'tools', 'direct'"
    )
    rewritten_query: str= Field(
        description= "Standalone, unambigious search/SQL query resolved from chat history"

    )

def router_node(state: AgentState) -> dict:
    # Forces the LLM to reply in strict JSON and parses the raw AIMessage
    # directly into a RouteDecision Python object (not a normal AIMessage).
    llm = get_llm(role='fast').with_structured_output(RouteDecision)
    raw_tools = state.get("active_tools") or []
    if isinstance(raw_tools, dict):
        enabled = {name for name, is_on in raw_tools.items() if is_on}
    else :
        enabled = set(raw_tools)
    has_db = bool(state.get("db_uri"))

    system_prompt = (
            "You are a routing supervisor for a multi-agent AI system.\n"
            f"Available capabilities right now: enabled_tools={list(enabled)}, sql_connected={has_db}.\n"
            "Pick the single best route:\n"
            "- 'sql': User asks about database tables, metrics, records, counts, or rows (ONLY if sql_connected=True).\n"
            "- 'rag': User asks about uploaded documents, manuals, policies, or private files (ONLY if 'rag_search' is in enabled_tools).\n"
            "- 'tools': User needs live web search or math calculations (ONLY if 'web_search' or 'calculator' is in enabled_tools).\n"
            "- 'direct': General conversation, coding help, or when the required tool/DB is disabled.\n"
            "Also rewrite the latest user message into a standalone query using prior chat context."
        )

    # Prepends routing rules to chat history; returns a RouteDecision instance
    # so you can access decision.route and decision.rewritten_query directly.
    decision: RouteDecision = llm.invoke(
        [SystemMessage(content=system_prompt)] + state['messages']
    )

    # Hard Python guardrail: blocks disabled tools/DB even if the LLM tries to pick them
    route =  decision.route 
    if route == "sql" and not has_db:
        route = "direct"
    elif route == "rag" and "rag_search" not in enabled:
        route = "direct"
    elif route == 'tools' and not (enabled & {"web_search", "calculator"}):
        route = "direct"

    return {
        "route" : route,
        "rewritten_query" : decision.rewritten_query
    }

